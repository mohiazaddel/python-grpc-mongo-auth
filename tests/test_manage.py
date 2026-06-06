from __future__ import annotations

from manage import build_parser


def test_manage_parser_accepts_runtime_commands() -> None:
    parser = build_parser()

    assert parser.parse_args(["serve"]).command == "serve"
    assert parser.parse_args(["sms-worker"]).command == "sms-worker"
    assert parser.parse_args(["init-db"]).command == "init-db"

