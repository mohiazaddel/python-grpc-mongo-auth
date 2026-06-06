from __future__ import annotations

from .container import Container


def main() -> None:
    Container().sms_consumer().start()


if __name__ == "__main__":
    main()
