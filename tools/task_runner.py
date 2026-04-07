from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from harbor.operator_surface import (
    render_db_settings,
    render_db_status,
    render_runtime_settings,
    render_smoke_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def cmd_show_settings() -> int:
    print(render_runtime_settings())
    return 0


def cmd_show_db_settings() -> int:
    print(render_db_settings())
    return 0


def cmd_db_status(check: bool) -> int:
    print(render_db_status(check=check))
    return 0


def cmd_smoke_local() -> int:
    payload = json.loads(render_smoke_payload())
    print("=== root ===")
    print(json.dumps(payload["root"], indent=2, sort_keys=True))
    print("=== healthz ===")
    print(json.dumps(payload["healthz"], indent=2, sort_keys=True))
    print("=== runtime ===")
    print(json.dumps(payload["runtime"], indent=2, sort_keys=True))
    print("=== db_status ===")
    print(json.dumps(payload["db_status"], indent=2, sort_keys=True))
    return 0


def cmd_quality_gates() -> int:
    subprocess.run([sys.executable, str(REPO_ROOT / "tools" / "run_quality_gates.py")], check=True)
    return 0


def cmd_run_dev() -> int:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "harbor.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload",
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Harbor local operator surface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("show-settings")
    subparsers.add_parser("show-db-settings")

    parser_db_status = subparsers.add_parser("db-status")
    parser_db_status.add_argument("--check", action="store_true")

    subparsers.add_parser("smoke-local")
    subparsers.add_parser("quality-gates")
    subparsers.add_parser("run-dev")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "show-settings":
        return cmd_show_settings()
    if args.command == "show-db-settings":
        return cmd_show_db_settings()
    if args.command == "db-status":
        return cmd_db_status(check=args.check)
    if args.command == "smoke-local":
        return cmd_smoke_local()
    if args.command == "quality-gates":
        return cmd_quality_gates()
    if args.command == "run-dev":
        return cmd_run_dev()

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
