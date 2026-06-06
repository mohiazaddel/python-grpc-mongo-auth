# Python gRPC Mongo Auth

OTP authentication backend built with Python, gRPC, MongoDB, RabbitMQ, and Kavenegar.

The service supports phone-based OTP login, durable SMS dispatch, JWT access tokens, refresh-token rotation, and role-based access control for `admin` and `user` roles.

## Architecture

The code follows a small DDD-style layered structure:

- `auth_service.domain`: OTP, token, and security rules
- `auth_service.application`: authentication use cases
- `auth_service.infrastructure`: MongoDB, RabbitMQ, and Kavenegar adapters
- `auth_service.interfaces.grpc`: gRPC transport layer
- `auth_service.container`: dependency-injection wiring
- `manage.py`: runtime command entrypoint

## Requirements Covered

- Python gRPC API
- MongoDB persistence
- RabbitMQ SMS queue with durable messages
- Kavenegar SMS delivery adapter
- Secure OTP storage using HMAC hashing and one-time use
- OTP expiry, resend cooldown, and attempt limit
- JWT access token plus refresh-token rotation
- `admin`, authenticated-user, and public gRPC methods
- Docker Compose for MongoDB, RabbitMQ, API, and SMS worker
- Unit tests for domain, repositories, gRPC access control, and messaging adapters

## Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Important variables:

- `JWT_SECRET`: long random secret for access tokens
- `OTP_PEPPER`: different long random secret for OTP HMAC hashing
- `KAVENEGAR_API_KEY`: Kavenegar API key used by the SMS worker
- `KAVENEGAR_SENDER`: sender line configured in Kavenegar
- `BOOTSTRAP_ADMIN_PHONE`: phone number that becomes `admin` after OTP verification
- `APP_ENV`: set to `production` to enforce strong `JWT_SECRET` and `OTP_PEPPER` values at startup

The application validates numeric settings, allowed roles, and production secret strength during startup. Do not use the default secrets outside local development.

## Run With Docker

```bash
docker compose up --build
```

Services:

- `auth`: gRPC API at `localhost:50051`
- `sms-worker`: consumes RabbitMQ messages and sends SMS through Kavenegar
- `mongo`: MongoDB storage
- `rabbitmq`: RabbitMQ broker and management UI at `localhost:15672`

The Compose stack includes MongoDB/RabbitMQ health checks, restart policies, and a non-root application container user.

## Local Development

Install dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Generate gRPC Python files:

```bash
python scripts/generate_proto.py
```

The test suite also generates these files automatically during collection.

Create MongoDB indexes:

```bash
python manage.py init-db
```

Run the API:

```bash
python manage.py serve
```

Run the SMS worker:

```bash
python manage.py sms-worker
```

## gRPC API

- `RequestOtp(phone)`: normalizes phone, creates a 6-digit OTP, stores only the OTP hash, and queues SMS
- `VerifyOtp(phone, otp)`: validates OTP, creates or loads the user, and returns an access/refresh token pair
- `RefreshToken(refresh_token)`: revokes the used refresh token and returns a new pair
- `PublicEndpoint()`: no authentication required
- `UserEndpoint()`: requires `authorization: Bearer <access_token>`
- `AdminEndpoint()`: requires `authorization: Bearer <access_token>` with role `admin`

## Tests

```bash
python -m pytest -q
```

To regenerate protobuf files manually, run:

```bash
python scripts/generate_proto.py
```

## Security Notes

- OTP values are generated with `secrets`, never stored in plaintext, and are checked with constant-time comparison.
- OTPs expire, can be used only once, and have a maximum attempt count.
- Refresh tokens are random, stored as hashes, rotated on every refresh, and protected with reuse detection.
- Access control is enforced in the gRPC interface through bearer-token metadata.
- A gRPC server interceptor emits defensive response metadata such as CSP, frame denial, referrer policy, permissions policy, and content-type sniffing protection.
- RabbitMQ publishes use durable messages, publisher confirms, and mandatory routing.
- RabbitMQ and Kavenegar adapter failures are wrapped as expected messaging errors for clearer handling.
