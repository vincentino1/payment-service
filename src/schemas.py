from __future__ import annotations

from dataclasses import dataclass

from .errors import ApiError


@dataclass(frozen=True)
class OrderItemIn:
    productId: str
    name: str
    unitPrice: int
    quantity: int


@dataclass(frozen=True)
class CreatePaymentIntentIn:
    userId: str
    currency: str
    items: list[OrderItemIn]


def parse_create_payment_intent(payload: dict) -> CreatePaymentIntentIn:
    if not isinstance(payload, dict):
        raise ApiError(code="VALIDATION_ERROR", message="invalid request body", status_code=400)

    user_id = payload.get("userId")
    currency = payload.get("currency", "USD")
    items = payload.get("items")

    if not isinstance(user_id, str) or not user_id:
        raise ApiError(code="VALIDATION_ERROR", message="userId is required", status_code=400)

    if not isinstance(currency, str) or len(currency) != 3:
        raise ApiError(code="VALIDATION_ERROR", message="currency must be 3-letter code", status_code=400)

    if not isinstance(items, list) or len(items) == 0:
        raise ApiError(code="VALIDATION_ERROR", message="items must be a non-empty list", status_code=400)

    parsed_items: list[OrderItemIn] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise ApiError(
                code="VALIDATION_ERROR",
                message="each item must be an object",
                status_code=400,
                details={"index": idx},
            )

        product_id = item.get("productId")
        name = item.get("name")
        unit_price = item.get("unitPrice")
        quantity = item.get("quantity")

        if not isinstance(product_id, str) or not product_id:
            raise ApiError(code="VALIDATION_ERROR", message="item.productId is required", status_code=400)
        if not isinstance(name, str) or not name:
            raise ApiError(code="VALIDATION_ERROR", message="item.name is required", status_code=400)
        if not isinstance(unit_price, int) or unit_price < 0:
            raise ApiError(code="VALIDATION_ERROR", message="item.unitPrice must be >= 0", status_code=400)
        if not isinstance(quantity, int) or quantity <= 0:
            raise ApiError(code="VALIDATION_ERROR", message="item.quantity must be > 0", status_code=400)

        parsed_items.append(
            OrderItemIn(productId=product_id, name=name, unitPrice=unit_price, quantity=quantity)
        )

    return CreatePaymentIntentIn(userId=user_id, currency=currency.upper(), items=parsed_items)
