from __future__ import annotations

import compileall
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_step(name: str, command: list[str]) -> None:
    print(f"\n=== {name} ===")
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def main() -> int:
    print("\n=== compileall ===")
    if not compileall.compile_dir(REPO_ROOT / "src", quiet=1):
        raise SystemExit(1)
    if not compileall.compile_dir(REPO_ROOT / "tests", quiet=1):
        raise SystemExit(1)
    if not compileall.compile_dir(REPO_ROOT / "tools", quiet=1):
        raise SystemExit(1)

    run_step("ruff", [sys.executable, "-m", "ruff", "check", "src", "tests", "tools"])
    run_step("pytest", [sys.executable, "-m", "pytest", "-q"])

    print("\nQuality gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
