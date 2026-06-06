from __future__ import annotations

import requests

from auth_service.config import Settings
from auth_service.application.ports import SmsMessage


class KavenegarClient:
    def __init__(self, settings: Settings, session: requests.Session | None = None) -> None:
        self.settings = settings
        self.session = session or requests.Session()

    def send_sms(self, message: SmsMessage) -> None:
        if not self.settings.kavenegar_api_key:
            raise RuntimeError("KAVENEGAR_API_KEY is required")
        url = f"https://api.kavenegar.com/v1/{self.settings.kavenegar_api_key}/sms/send.json"
        response = self.session.post(
            url,
            data={
                "receptor": message.phone,
                "sender": self.settings.kavenegar_sender,
                "message": message.text,
            },
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("return", {}).get("status") != 200:
            raise RuntimeError(f"kavenegar rejected sms: {payload.get('return')}")
