from __future__ import annotations

from concurrent import futures

import grpc

from proto import auth_pb2_grpc

from .container import Container


def serve() -> None:
    container = Container()
    settings = container.settings()
    store = container.store()
    store.ensure_indexes()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=16))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(container.grpc_auth_service(), server)
    server.add_insecure_port(f"{settings.grpc_host}:{settings.grpc_port}")
    server.start()
    print(f"Auth gRPC server listening on {settings.grpc_host}:{settings.grpc_port}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
