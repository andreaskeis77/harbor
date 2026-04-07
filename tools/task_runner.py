from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Harbor task runner.")
    parser.add_argument(
        "command",
        choices=("quality-gates", "show-settings", "smoke-local", "run-dev"),
        help="Task to execute.",
    )
    return parser


def run_subprocess(args: list[str]) -> int:
    return subprocess.call(args, cwd=REPO_ROOT)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "quality-gates":
        return run_subprocess([sys.executable, "tools/run_quality_gates.py"])
    if args.command in {"show-settings", "smoke-local", "run-dev"}:
        return run_subprocess([sys.executable, "-m", "harbor.operator_surface", args.command])

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
