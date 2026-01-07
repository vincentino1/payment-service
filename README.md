# checkout-payment-service

Python/Flask microservice for checkout + payment.

## What’s included
- Flask app factory
- PostgreSQL persistence (SQLAlchemy)
- Payment intent + capture flow (simulated gateway)
- Idempotency key support for capture
- Migrations via Alembic
- Pytest test suite
- Postman collection + environment (see `postman/`)

## Prereqs
- Python 3.11+ (3.10 should work)
- Postgres reachable from your machine

## Configure
Create a virtualenv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set env vars (example):

```bash
export FLASK_ENV=development
export PORT=5002
export DATABASE_URL='postgresql+psycopg://devEccomerce:devEccomerce$@localhost:5432/vogueThreads'
export JWT_JWKS_URL=''   # optional (not enforced yet)
```

## Database
This service uses these tables:
- `orders`
- `order_items`
- `payments`
- `idempotency_keys`

Run migrations:

```bash
alembic upgrade head
```

## Run

```bash
python -m src.server
```

Health check:

```bash
curl -s http://localhost:5002/health
```

## Postman
Import these files into Postman:
- `postman/checkout-payment-service.postman_collection.json`
- `postman/checkout-payment-service.postman_environment.json`

Set the active environment to **checkout-payment-service (local)**.

Suggested flow:
1. **GET /health**
2. **POST /api/payments/intents** (stores `paymentId` automatically)
3. **POST /api/payments/intents/{{paymentId}}/capture**
4. **GET /api/payments/{{paymentId}}`

## API (initial)

### Health
- `GET /health`

### Payments
- `POST /api/payments/intents`
- `POST /api/payments/intents/<paymentId>/capture`
- `GET /api/payments/<paymentId>`

See the route definitions in `src/routes/payments.py`.
