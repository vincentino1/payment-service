from __future__ import annotations

import hashlib
import json
import uuid

from flask import Blueprint, request
from sqlalchemy import select

from ..db import session_scope
from ..errors import ApiError
from ..models import IdempotencyKey, Order, OrderItem, OrderStatus, Payment, PaymentStatus
from ..schemas import parse_create_payment_intent

bp = Blueprint("payments", __name__, url_prefix="/api")


def _hash_request(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _payment_to_dict(p: Payment) -> dict:
    return {
        "id": str(p.id),
        "orderId": str(p.order_id),
        "provider": p.provider,
        "status": p.status.value,
        "amount": p.amount,
        "currency": p.currency,
    }


def _order_to_dict(o: Order) -> dict:
    return {
        "id": str(o.id),
        "userId": o.user_id,
        "currency": o.currency,
        "totalAmount": o.total_amount,
        "status": o.status.value,
    }


@bp.post("/payments/intents")
def create_payment_intent():
    body = parse_create_payment_intent(request.get_json(silent=True) or {})

    total = 0
    for item in body.items:
        total += item.unitPrice * item.quantity

    with session_scope() as session:
        order = Order(user_id=body.userId, currency=body.currency, total_amount=total, status=OrderStatus.CREATED)
        session.add(order)
        session.flush()

        for item in body.items:
            session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item.productId,
                    name=item.name,
                    unit_price=item.unitPrice,
                    quantity=item.quantity,
                    line_total=item.unitPrice * item.quantity,
                )
            )

        payment = Payment(
            order_id=order.id,
            provider="SIMULATED",
            status=PaymentStatus.REQUIRES_CAPTURE,
            amount=total,
            currency=body.currency,
            provider_payment_id=f"sim_{uuid.uuid4().hex}",
        )
        session.add(payment)
        session.flush()

        out = {"order": _order_to_dict(order), "payment": _payment_to_dict(payment)}

    return out, 201


@bp.post("/payments/intents/<payment_id>/capture")
def capture_payment(payment_id: str):
    idempotency_key = request.headers.get("Idempotency-Key")
    payload = request.get_json(silent=True) or {}

    if not idempotency_key:
        raise ApiError(code="MISSING_IDEMPOTENCY_KEY", message="Idempotency-Key header required", status_code=400)

    scope = f"capture:{payment_id}"
    req_hash = _hash_request(payload)

    with session_scope() as session:
        existing = session.execute(
            select(IdempotencyKey).where(IdempotencyKey.key == idempotency_key, IdempotencyKey.scope == scope)
        ).scalar_one_or_none()
        if existing:
            if existing.request_hash != req_hash:
                raise ApiError(
                    code="IDEMPOTENCY_KEY_REUSED",
                    message="Idempotency-Key already used with different request",
                    status_code=409,
                )
            return json.loads(existing.response_json), 200

        payment = session.get(Payment, uuid.UUID(payment_id))
        if not payment:
            raise ApiError(code="NOT_FOUND", message="payment not found", status_code=404)

        order = session.get(Order, payment.order_id)
        if not order:
            raise ApiError(code="NOT_FOUND", message="order not found", status_code=404)

        # Simulated gateway rule: fail if amount ends with 13 cents
        if payment.amount % 100 == 13:
            payment.status = PaymentStatus.FAILED
            order.status = OrderStatus.FAILED
        else:
            payment.status = PaymentStatus.SUCCEEDED
            order.status = OrderStatus.PAID

        session.flush()

        response = {"payment": _payment_to_dict(payment), "order": _order_to_dict(order)}
        session.add(
            IdempotencyKey(
                key=idempotency_key,
                scope=scope,
                request_hash=req_hash,
                response_json=json.dumps(response),
            )
        )

        return response, 200


@bp.get("/payments/<payment_id>")
def get_payment(payment_id: str):
    with session_scope() as session:
        payment = session.get(Payment, uuid.UUID(payment_id))
        if not payment:
            raise ApiError(code="NOT_FOUND", message="payment not found", status_code=404)
        order = session.get(Order, payment.order_id)
        if not order:
            raise ApiError(code="NOT_FOUND", message="order not found", status_code=404)

        return {"payment": _payment_to_dict(payment), "order": _order_to_dict(order)}
