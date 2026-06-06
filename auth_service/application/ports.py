from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SmsMessage:
    phone: str
    text: str


class SmsPublisher(Protocol):
    def publish(self, message: SmsMessage) -> None:
        ...

