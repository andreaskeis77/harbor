from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_step(name: str, command: list[str]) -> None:
    print(f"\n=== {name} ===")
    completed = subprocess.run(command, cwd=REPO_ROOT)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    python = sys.executable

    run_step("compileall", [python, "-m", "compileall", "src", "tests", "tools"])
    run_step("ruff", [python, "-m", "ruff", "check", "src", "tests", "tools"])
    run_step("pytest", [python, "-m", "pytest"])

    print("\nQuality gates passed.")


if __name__ == "__main__":
    main()
