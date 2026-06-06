from __future__ import annotations

import argparse

from injection import Injection
from auth_service.interfaces.grpc.server import serve

injection = Injection()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the auth service")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("serve", help="Run the gRPC API server")
    subcommands.add_parser("sms-worker", help="Run the RabbitMQ SMS worker")
    subcommands.add_parser("init-db", help="Create MongoDB indexes")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "serve":
        serve(injection)
        return
    if args.command == "sms-worker":
        from auth_service.infrastructure.messaging import RabbitSmsConsumer

        injection.get(RabbitSmsConsumer).start()
        return
    if args.command == "init-db":
        from auth_service.infrastructure.database import MongoStore

        injection.get(MongoStore).ensure_indexes()
        print("MongoDB indexes are ready", flush=True)
        return

    raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
