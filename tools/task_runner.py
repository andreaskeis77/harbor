from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from harbor.config import get_settings
from harbor.operator_surface import (
    database_status_for_operator,
    print_json,
    show_db_settings_payload,
    show_settings_payload,
    smoke_handbook_slice_payload,
    smoke_local_payload,
    smoke_project_slice_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_subprocess(args: list[str]) -> int:
    completed = subprocess.run(args, cwd=REPO_ROOT, check=False)
    return completed.returncode


def command_run_dev() -> int:
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
    return run_subprocess(command)


def command_quality_gates() -> int:
    return run_subprocess([sys.executable, str(REPO_ROOT / "tools" / "run_quality_gates.py")])


def command_show_settings() -> int:
    print_json(show_settings_payload())
    return 0


def command_show_db_settings() -> int:
    print_json(show_db_settings_payload())
    return 0


def command_db_status() -> int:
    print_json(database_status_for_operator())
    return 0


def command_smoke_local() -> int:
    payload = smoke_local_payload()
    print("=== root ===")
    print_json(payload["root"])
    print("=== healthz ===")
    print_json(payload["healthz"])
    print("=== runtime ===")
    print_json(payload["runtime"])
    return 0


def command_smoke_project_slice() -> int:
    print_json(smoke_project_slice_payload())
    return 0


def command_smoke_handbook_slice() -> int:
    print_json(smoke_handbook_slice_payload())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Harbor task runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("run-dev")
    subparsers.add_parser("quality-gates")
    subparsers.add_parser("show-settings")
    subparsers.add_parser("show-db-settings")
    subparsers.add_parser("db-status")
    subparsers.add_parser("smoke-local")
    subparsers.add_parser("smoke-project-slice")
    subparsers.add_parser("smoke-handbook-slice")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    command_map = {
        "run-dev": command_run_dev,
        "quality-gates": command_quality_gates,
        "show-settings": command_show_settings,
        "show-db-settings": command_show_db_settings,
        "db-status": command_db_status,
        "smoke-local": command_smoke_local,
        "smoke-project-slice": command_smoke_project_slice,
        "smoke-handbook-slice": command_smoke_handbook_slice,
    }
    return command_map[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
