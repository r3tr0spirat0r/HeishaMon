import os
import subprocess
from pathlib import Path
from typing import Mapping


DEFAULT_VERSION = "Local build"


def get_build_version(project_dir: Path, environ: Mapping[str, str] | None = None) -> str:
    env = os.environ if environ is None else environ
    override = env.get("HEISHAMON_VERSION", "").strip()
    if override:
        return override

    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=project_dir,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return DEFAULT_VERSION

    version = result.stdout.strip()
    return version or DEFAULT_VERSION


def make_version_build_flag(version: str) -> str:
    return f'-DHEISHAMON_VERSION=\\"{_escape_build_flag_value(version)}\\"'


def _escape_build_flag_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def configure_platformio_version() -> None:
    try:
        Import("env")  # type: ignore[name-defined]  # noqa: F821
    except NameError:
        return

    project_dir = Path(env["PROJECT_DIR"])  # type: ignore[name-defined]  # noqa: F821
    version = get_build_version(project_dir)
    env.Append(BUILD_FLAGS=[make_version_build_flag(version)])  # type: ignore[name-defined]  # noqa: F821
    print(f"Set HEISHAMON_VERSION to {version}")


configure_platformio_version()


if __name__ == "__main__":
    print(make_version_build_flag(get_build_version(Path(__file__).resolve().parents[1])))
