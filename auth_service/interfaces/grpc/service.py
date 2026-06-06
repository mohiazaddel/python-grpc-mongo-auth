from __future__ import annotations

import grpc

from proto import auth_pb2, auth_pb2_grpc

from auth_service.application.auth import AuthApplicationService
from auth_service.errors import AuthError, InvalidCredentials, MessagingError, PermissionDenied, RateLimited


def metadata_value(context: grpc.ServicerContext, key: str) -> str | None:
    for item_key, item_value in context.invocation_metadata():
        if item_key.lower() == key.lower():
            return item_value
    return None


def abort_for_error(context: grpc.ServicerContext, exc: Exception) -> None:
    if isinstance(exc, RateLimited):
        context.abort(grpc.StatusCode.RESOURCE_EXHAUSTED, str(exc))
    if isinstance(exc, PermissionDenied):
        context.abort(grpc.StatusCode.PERMISSION_DENIED, str(exc))
    if isinstance(exc, InvalidCredentials):
        context.abort(grpc.StatusCode.UNAUTHENTICATED, str(exc))
    if isinstance(exc, MessagingError):
        context.abort(grpc.StatusCode.UNAVAILABLE, str(exc))
    if isinstance(exc, AuthError):
        context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))
    context.abort(grpc.StatusCode.INTERNAL, "internal error")


class AuthGrpcService(auth_pb2_grpc.AuthServiceServicer):
    def __init__(self, auth_service: AuthApplicationService) -> None:
        self.auth_service = auth_service

    def RequestOtp(self, request, context):
        try:
            self.auth_service.request_otp(request.phone)
            return auth_pb2.RequestOtpResponse(accepted=True, message="otp queued")
        except Exception as exc:
            abort_for_error(context, exc)

    def VerifyOtp(self, request, context):
        try:
            pair = self.auth_service.verify_otp(request.phone, request.otp)
            return auth_pb2.TokenResponse(
                access_token=pair["access_token"],
                refresh_token=pair["refresh_token"],
                token_type="Bearer",
                expires_in=pair["expires_in"],
                role=pair["role"],
            )
        except Exception as exc:
            abort_for_error(context, exc)

    def RefreshToken(self, request, context):
        try:
            pair = self.auth_service.refresh(request.refresh_token)
            return auth_pb2.TokenResponse(
                access_token=pair["access_token"],
                refresh_token=pair["refresh_token"],
                token_type="Bearer",
                expires_in=pair["expires_in"],
                role=pair["role"],
            )
        except Exception as exc:
            abort_for_error(context, exc)

    def PublicEndpoint(self, request, context):
        return auth_pb2.AccessResponse(message="public access granted")

    def UserEndpoint(self, request, context):
        try:
            self.auth_service.authorize(metadata_value(context, "authorization"))
            return auth_pb2.AccessResponse(message="authenticated user access granted")
        except Exception as exc:
            abort_for_error(context, exc)

    def AdminEndpoint(self, request, context):
        try:
            self.auth_service.authorize(metadata_value(context, "authorization"), required_role="admin")
            return auth_pb2.AccessResponse(message="admin access granted")
        except Exception as exc:
            abort_for_error(context, exc)

