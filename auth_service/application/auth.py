from __future__ import annotations

from typing import Any

from auth_service.config import Settings
from auth_service.domain.auth import OtpService, TokenService
from auth_service.domain.ports import UserRepository
from auth_service.domain.security import normalize_phone

from .ports import SmsMessage, SmsPublisher


class AuthApplicationService:
    def __init__(
        self,
        settings: Settings,
        users: UserRepository,
        otp_service: OtpService,
        token_service: TokenService,
        sms_publisher: SmsPublisher,
    ) -> None:
        self.settings = settings
        self.users = users
        self.otp_service = otp_service
        self.token_service = token_service
        self.sms_publisher = sms_publisher

    def request_otp(self, phone: str) -> None:
        phone = normalize_phone(phone)
        otp = self.otp_service.create_otp(phone)
        self.sms_publisher.publish(SmsMessage(phone=phone, text=f"Your verification code is {otp}"))

    def verify_otp(self, phone: str, otp: str) -> dict[str, Any]:
        phone = normalize_phone(phone)
        self.otp_service.verify_otp(phone, otp)
        user = self.users.get_or_create_by_phone(phone, self._role_for_phone(phone))
        return self.token_service.issue_pair(user)

    def refresh(self, refresh_token: str) -> dict[str, Any]:
        return self.token_service.refresh(refresh_token)

    def authorize(self, authorization: str | None, required_role: str | None = None) -> dict[str, Any]:
        return self.token_service.verify_access(authorization, required_role)

    def _role_for_phone(self, phone: str) -> str:
        if self.settings.bootstrap_admin_phone and phone == normalize_phone(self.settings.bootstrap_admin_phone):
            return "admin"
        return self.settings.default_user_role
