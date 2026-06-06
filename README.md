# Python gRPC Mongo Auth

Authentication backend with Python gRPC, MongoDB, RabbitMQ-backed SMS dispatch, Kavenegar delivery, OTP login, JWT access tokens, refresh-token rotation, and role-based access control.

The code is split into explicit layers:

- `repositories`: MongoDB persistence boundaries
- `services`: OTP, token, and authentication application logic
- `messaging` and `kavenegar`: infrastructure adapters
- `grpc_service`: transport/API layer
- `container`: dependency-injector wiring

## Services

- `auth`: gRPC API on `localhost:50051`
- `sms-worker`: consumes RabbitMQ OTP SMS jobs and sends them through Kavenegar
- `mongo`: user, OTP, and refresh-token persistence
- `rabbitmq`: durable SMS queue, management UI on `localhost:15672`

## Run

```bash
cp .env.example .env
docker compose up --build
```

Set strong `JWT_SECRET` and `OTP_PEPPER` values before using this outside local testing.
Use `BOOTSTRAP_ADMIN_PHONE` to make one OTP-verified phone an admin for access-control testing.

## API

- `RequestOtp(phone)`: creates a short-lived OTP and queues SMS delivery
- `VerifyOtp(phone, otp)`: validates OTP, creates user if needed, returns access and refresh tokens
- `RefreshToken(refresh_token)`: rotates refresh token and returns a new token pair
- `PublicEndpoint()`: public test method
- `UserEndpoint()`: requires `authorization: Bearer <access_token>`
- `AdminEndpoint()`: requires an authenticated user with role `admin`

## Tests

```bash
python -m pip install -r requirements-dev.txt
python scripts/generate_proto.py
pytest
```
