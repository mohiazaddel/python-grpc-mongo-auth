from __future__ import annotations

from unittest.mock import Mock

from auth_service.interfaces.grpc.security import SECURITY_METADATA, send_security_metadata


def test_security_metadata_contains_defensive_headers() -> None:
    metadata = dict(SECURITY_METADATA)

    assert metadata["x-content-type-options"] == "nosniff"
    assert metadata["x-frame-options"] == "DENY"
    assert metadata["x-xss-protection"] == "0"
    assert "default-src 'none'" in metadata["content-security-policy"]
    assert metadata["referrer-policy"] == "no-referrer"
    assert "camera=()" in metadata["permissions-policy"]


def test_send_security_metadata_sets_initial_metadata() -> None:
    context = Mock()

    send_security_metadata(context)

    context.send_initial_metadata.assert_called_once_with(SECURITY_METADATA)
