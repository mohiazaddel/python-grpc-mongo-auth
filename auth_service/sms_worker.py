from __future__ import annotations

from injection import Injection

from .infrastructure.messaging import RabbitSmsConsumer


def main() -> None:
    Injection().get(RabbitSmsConsumer).start()


if __name__ == "__main__":
    main()
