from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> int:
    return subprocess.run(command, cwd=REPO_ROOT).returncode


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python .\\tools\\task_runner.py [quality-gates|run-dev|smoke]")
        return 2

    task = argv[1]
    python = sys.executable

    if task == "quality-gates":
        return run([python, str(REPO_ROOT / "tools" / "run_quality_gates.py")])

    if task == "run-dev":
        return run(
            [
                python,
                "-m",
                "uvicorn",
                "harbor.app:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                "--reload",
            ]
        )

    if task == "smoke":
        return run(
            [
                python,
                "-c",
                (
                    "import urllib.request; "
                    "print(urllib.request.urlopen('http://127.0.0.1:8000/healthz').read().decode())"
                ),
            ]
        )

    print(f"Unknown task: {task}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
