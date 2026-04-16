from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def print_step(message: str) -> None:
    print(f"==> {message}")


def run_command(args: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    completed = subprocess.run(args, cwd=cwd, env=env, check=False)
    if completed.returncode != 0:
        joined = " ".join(args)
        raise RuntimeError(f"command failed: {joined}")


def resolve_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_venv_python(venv_root: Path) -> Path:
    if os.name == "nt":
        return venv_root / "Scripts" / "python.exe"
    return venv_root / "bin" / "python"


def build_activation_hint(venv_root: Path) -> str:
    if os.name == "nt":
        return str(venv_root / "Scripts" / "activate.bat")
    return f"source {venv_root / 'bin' / 'activate'}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize local development environment.")
    parser.add_argument("--venv-path", default=".venv", help="virtual environment path relative to repo root")
    parser.add_argument("--run-checks", action="store_true", help="run compileall and pytest after install")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root()
    system_python = Path(sys.executable).resolve()
    venv_root = (repo_root / args.venv_path).resolve() if not Path(args.venv_path).is_absolute() else Path(args.venv_path).resolve()
    venv_python = resolve_venv_python(venv_root)
    requirements_path = repo_root / "requirements.txt"

    print_step(f"Using system Python: {system_python}")

    if not venv_root.exists():
        print_step(f"Creating virtual environment: {venv_root}")
        run_command([str(system_python), "-m", "venv", str(venv_root)])
    else:
        print_step(f"Reusing existing virtual environment: {venv_root}")

    if not venv_python.exists():
        raise FileNotFoundError(f"virtual environment python not found: {venv_python}")
    if not requirements_path.exists():
        raise FileNotFoundError(f"requirements.txt was not found: {requirements_path}")

    print_step("Upgrading pip")
    run_command([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])

    print_step("Installing dependencies from requirements.txt")
    run_command([str(venv_python), "-m", "pip", "install", "-r", str(requirements_path)])

    if args.run_checks:
        print_step("Running syntax checks")
        run_command([str(venv_python), "-m", "compileall", "src", "tests"], cwd=repo_root)

        print_step("Running pytest")
        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo_root)
        run_command([str(venv_python), "-m", "pytest", "-q"], cwd=repo_root, env=env)

    print()
    print("Local environment setup completed.")
    print(f"Activation hint: {build_activation_hint(venv_root)}")
    print(f"Run tests with: {venv_python} -m pytest -q")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
