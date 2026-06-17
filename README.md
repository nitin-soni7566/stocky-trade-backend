# intraday-trading-backend

Phase 1 FastAPI backend for an automated trading mobile app. This version supports paper trading only.

## Features

- JWT user registration, login, and current-user API
- Encrypted Definedge broker credentials using Fernet
- Broker token generation and profile fetch
- NIFTY 50 list and Definedge LTP lookup
- Paper bot start/stop flow with one BUY entry and SELL exit
- Orders, positions, and today's realized P&L
- Async SQLAlchemy, PostgreSQL, Alembic, and Docker

## Setup

1. Create environment file:

```bash
cp .env.example .env
```

2. Generate a Fernet key and set `ENCRYPTION_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

3. Start Postgres and Redis with Docker:

```bash
docker compose up -d db redis
```

4. Run migrations from your local environment:

```bash
alembic upgrade head
```

5. Start the API locally:

```bash
uvicorn app.main:app --reload
```

6. Open API docs:

```text
http://localhost:8000/docs
```

## Full Docker Stack

To run the API, Postgres, and Redis together in Docker:

```bash
docker compose up --build
```

Then run migrations inside the API container:

```bash
docker compose exec api alembic upgrade head
```

## Local Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

For local development, `DATABASE_URL` should point to `localhost:5432` and `REDIS_URL` should point to `localhost:6379`. When the API runs inside Docker Compose, those values are overridden to use the Docker service names `db` and `redis`.

## API Prefix

All app endpoints are under `/api/v1`.

## Definedge OTP Flow

1. Save broker credentials:

```bash
curl --location 'http://localhost:8000/api/v1/broker/credentials' \
  --header 'Authorization: Bearer <app_jwt>' \
  --header 'Content-Type: application/json' \
  --data '{"api_key":"<definedge_api_key>","api_secret":"<definedge_api_secret>"}'
```

2. Generate OTP:

```bash
curl --location --request POST 'http://localhost:8000/api/v1/broker/token/generate' \
  --header 'Authorization: Bearer <app_jwt>'
```

3. Verify OTP and store broker access token encrypted:

```bash
curl --location 'http://localhost:8000/api/v1/broker/token/verify' \
  --header 'Authorization: Bearer <app_jwt>' \
  --header 'Content-Type: application/json' \
  --data '{"otp_token":"<otp_token>","otp":"<otp_code>"}'
```

## Safety

`ENABLE_LIVE_TRADING=false` by default. `DefinedgeClient.place_order()` raises `403` unless this flag is enabled, and Phase 1 bot logic rejects live trading.
