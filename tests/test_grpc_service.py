from __future__ import annotations

from unittest.mock import Mock

import grpc
import pytest

from auth_service.application.auth import AuthApplicationService
from auth_service.domain.auth import OtpService, TokenService
from auth_service.interfaces.grpc.service import AuthGrpcService
from proto import auth_pb2


class FakeContext:
    def __init__(self, metadata=None) -> None:
        self._metadata = metadata or []

    def invocation_metadata(self):
        return self._metadata

    def abort(self, code, details):
        raise grpc.RpcError(f"{code.name}: {details}")


def test_public_endpoint_allows_anonymous(settings, store) -> None:
    app = AuthApplicationService(settings, Mock(), Mock(), Mock(), Mock())
    service = AuthGrpcService(app)
    response = service.PublicEndpoint(auth_pb2.Empty(), FakeContext())
    assert response.message == "public access granted"


def test_user_endpoint_requires_bearer_token(settings, users, otps, refresh_tokens) -> None:
    app = AuthApplicationService(
        settings,
        users,
        OtpService(otps, settings),
        TokenService(users, refresh_tokens, settings),
        Mock(),
    )
    service = AuthGrpcService(app)
    with pytest.raises(grpc.RpcError):
        service.UserEndpoint(auth_pb2.Empty(), FakeContext())


def test_admin_endpoint_requires_admin_role(settings, users, otps, refresh_tokens) -> None:
    user = users.get_or_create_by_phone("+989123456789", "user")
    token_service = TokenService(users, refresh_tokens, settings)
    pair = token_service.issue_pair(user)
    app = AuthApplicationService(settings, users, OtpService(otps, settings), token_service, Mock())
    service = AuthGrpcService(app)

    with pytest.raises(grpc.RpcError):
        service.AdminEndpoint(auth_pb2.Empty(), FakeContext([("authorization", f"Bearer {pair['access_token']}")]))
