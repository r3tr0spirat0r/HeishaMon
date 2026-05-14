import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from set_heishamon_version import (  # noqa: E402
    get_build_version,
    make_version_build_flag,
)


class VersionHeaderTests(unittest.TestCase):
    def test_make_version_build_flag_defines_cpp_string_literal(self):
        self.assertEqual(
            make_version_build_flag("v4.1.3"), '-DHEISHAMON_VERSION=\\"v4.1.3\\"'
        )

    def test_get_build_version_prefers_environment_override(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env = os.environ.copy()
            env["HEISHAMON_VERSION"] = "v9.9.9-custom"

            self.assertEqual(get_build_version(Path(temp_dir), env), "v9.9.9-custom")

    def test_get_build_version_uses_nearest_git_tag(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(
                ["git", "config", "user.email", "test@example.invalid"],
                cwd=repo,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
            )
            (repo / "file.txt").write_text("one\n", encoding="utf-8")
            subprocess.run(["git", "add", "file.txt"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "tag", "v4.1.3"], cwd=repo, check=True)
            (repo / "file.txt").write_text("two\n", encoding="utf-8")
            subprocess.run(["git", "commit", "-am", "patch"], cwd=repo, check=True, stdout=subprocess.DEVNULL)

            self.assertEqual(get_build_version(repo, {}), "v4.1.3")


if __name__ == "__main__":
    unittest.main()
