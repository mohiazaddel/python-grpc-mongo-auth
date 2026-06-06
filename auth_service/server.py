from __future__ import annotations

from .interfaces.grpc.server import serve as grpc_serve
from injection import Injection


def serve() -> None:
    grpc_serve(Injection())


if __name__ == "__main__":
    serve()
