from __future__ import annotations

from concurrent import futures

import grpc

from proto import auth_pb2_grpc

from auth_service.config import Settings
from auth_service.infrastructure.database import MongoStore
from auth_service.interfaces.grpc.security import SecurityMetadataInterceptor
from auth_service.interfaces.grpc.service import AuthGrpcService
from injection import Injection


def create_server(injection: Injection) -> grpc.Server:
    settings = injection.get(Settings)
    injection.get(MongoStore).ensure_indexes()
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=16),
        interceptors=(SecurityMetadataInterceptor(),),
    )
    auth_pb2_grpc.add_AuthServiceServicer_to_server(injection.get(AuthGrpcService), server)
    server.add_insecure_port(f"{settings.grpc_host}:{settings.grpc_port}")
    return server


def serve(injection: Injection) -> None:
    settings = injection.get(Settings)
    server = create_server(injection)
    server.start()
    print(f"Auth gRPC server listening on {settings.grpc_host}:{settings.grpc_port}", flush=True)
    server.wait_for_termination()
