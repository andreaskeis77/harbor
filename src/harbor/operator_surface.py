from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from harbor.app import app
from harbor.config import get_settings
from harbor.runtime import runtime_summary


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def cmd_show_settings() -> int:
    payload = runtime_summary(get_settings())
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_smoke_local() -> int:
    with TestClient(app) as client:
        root_response = client.get("/")
        health_response = client.get("/healthz")
        runtime_response = client.get("/runtime")

    if root_response.status_code != 200:
        raise SystemExit(f"Root smoke failed: {root_response.status_code}")
    if health_response.status_code != 200:
        raise SystemExit(f"Health smoke failed: {health_response.status_code}")
    if runtime_response.status_code != 200:
        raise SystemExit(f"Runtime smoke failed: {runtime_response.status_code}")

    print("=== root ===")
    print(json.dumps(root_response.json(), indent=2, sort_keys=True))
    print("=== healthz ===")
    print(json.dumps(health_response.json(), indent=2, sort_keys=True))
    print("=== runtime ===")
    print(json.dumps(runtime_response.json(), indent=2, sort_keys=True))
    return 0


def cmd_run_dev() -> int:
    settings = get_settings()
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "harbor.app:app",
        "--host",
        settings.host,
        "--port",
        str(settings.port),
    ]
    if settings.reload:
        command.append("--reload")
    return subprocess.call(command, cwd=_repo_root())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Harbor local operator surface.")
    parser.add_argument(
        "command",
        choices=("show-settings", "smoke-local", "run-dev"),
        help="Operator command to execute.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "show-settings":
        return cmd_show_settings()
    if args.command == "smoke-local":
        return cmd_smoke_local()
    if args.command == "run-dev":
        return cmd_run_dev()

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
