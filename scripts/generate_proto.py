from __future__ import annotations

from pathlib import Path

from grpc_tools import protoc


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    return protoc.main(
        [
            "grpc_tools.protoc",
            f"-I{ROOT}",
            f"--python_out={ROOT}",
            f"--grpc_python_out={ROOT}",
            str(ROOT / "proto" / "auth.proto"),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())

