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
    print("\n=== compileall (syntax check) ===")
    ok = compileall.compile_dir(str(REPO_ROOT / "src"), force=False, quiet=1)
    ok = compileall.compile_dir(str(REPO_ROOT / "tests"), force=False, quiet=1) and ok
    ok = compileall.compile_dir(str(REPO_ROOT / "tools"), force=False, quiet=1) and ok
    if not ok:
        print("compileall FAILED — syntax errors detected")
        return 1

    run_step("ruff (lint)", [sys.executable, "-m", "ruff", "check", "src", "tests", "tools"])
    run_step(
        "pytest (tests + coverage gate)",
        [sys.executable, "-m", "pytest", "-q"],
    )

    print("\nAll quality gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
