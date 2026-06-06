from __future__ import annotations

import requests

from auth_service.application.ports import SmsMessage
from auth_service.config import Settings
from auth_service.errors import MessagingError


class KavenegarClient:
    def __init__(self, settings: Settings, session: requests.Session | None = None) -> None:
        self.settings = settings
        self.session = session or requests.Session()

    def send_sms(self, message: SmsMessage) -> None:
        if not self.settings.kavenegar_api_key:
            raise MessagingError("KAVENEGAR_API_KEY is required")
        url = f"https://api.kavenegar.com/v1/{self.settings.kavenegar_api_key}/sms/send.json"
        try:
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
        except requests.RequestException as exc:
            raise MessagingError("failed to send sms through kavenegar") from exc
        except ValueError as exc:
            raise MessagingError("kavenegar returned an invalid response") from exc

        if payload.get("return", {}).get("status") != 200:
            raise MessagingError("kavenegar rejected sms")
