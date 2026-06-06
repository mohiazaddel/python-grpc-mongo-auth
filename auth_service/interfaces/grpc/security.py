from __future__ import annotations

from collections.abc import Callable
from typing import Any

import grpc


SECURITY_METADATA: tuple[tuple[str, str], ...] = (
    ("x-content-type-options", "nosniff"),
    ("x-frame-options", "DENY"),
    ("x-xss-protection", "0"),
    ("content-security-policy", "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"),
    ("referrer-policy", "no-referrer"),
    ("permissions-policy", "camera=(), geolocation=(), microphone=()"),
)


def send_security_metadata(context: grpc.ServicerContext) -> None:
    context.send_initial_metadata(SECURITY_METADATA)


class SecurityMetadataInterceptor(grpc.ServerInterceptor):
    def intercept_service(
        self,
        continuation: Callable[[grpc.HandlerCallDetails], grpc.RpcMethodHandler | None],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler | None:
        handler = continuation(handler_call_details)
        if handler is None:
            return None

        if handler.unary_unary:
            return grpc.unary_unary_rpc_method_handler(
                self._wrap_unary_unary(handler.unary_unary),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if handler.unary_stream:
            return grpc.unary_stream_rpc_method_handler(
                self._wrap_unary_stream(handler.unary_stream),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if handler.stream_unary:
            return grpc.stream_unary_rpc_method_handler(
                self._wrap_stream_unary(handler.stream_unary),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if handler.stream_stream:
            return grpc.stream_stream_rpc_method_handler(
                self._wrap_stream_stream(handler.stream_stream),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        return handler

    def _wrap_unary_unary(self, behavior: Callable[[Any, grpc.ServicerContext], Any]) -> Callable:
        def wrapped(request: Any, context: grpc.ServicerContext) -> Any:
            send_security_metadata(context)
            return behavior(request, context)

        return wrapped

    def _wrap_unary_stream(self, behavior: Callable[[Any, grpc.ServicerContext], Any]) -> Callable:
        def wrapped(request: Any, context: grpc.ServicerContext) -> Any:
            send_security_metadata(context)
            return behavior(request, context)

        return wrapped

    def _wrap_stream_unary(self, behavior: Callable[[Any, grpc.ServicerContext], Any]) -> Callable:
        def wrapped(request_iterator: Any, context: grpc.ServicerContext) -> Any:
            send_security_metadata(context)
            return behavior(request_iterator, context)

        return wrapped

    def _wrap_stream_stream(self, behavior: Callable[[Any, grpc.ServicerContext], Any]) -> Callable:
        def wrapped(request_iterator: Any, context: grpc.ServicerContext) -> Any:
            send_security_metadata(context)
            return behavior(request_iterator, context)

        return wrapped
