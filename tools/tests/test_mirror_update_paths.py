from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def run_patch_capture(repo_dir: Path, patch_path: Path) -> bool:
    run(["git", "add", "-N", "."], cwd=repo_dir)
    diff = subprocess.run(["git", "diff", "--quiet", "--", "."], cwd=repo_dir, check=False)
    if diff.returncode == 0:
        return False
    with open(patch_path, "w", encoding="utf-8") as handle:
        subprocess.run(
            ["git", "diff", "--binary", "--full-index", "--", "."],
            cwd=repo_dir,
            check=True,
            text=True,
            stdout=handle,
        )
    return True


def run_publish(repo_dir: Path, patch_path: Path) -> str:
    run(["git", "config", "user.name", "github-actions[bot]"], cwd=repo_dir)
    run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=repo_dir)
    run(["git", "reset", "--hard", "HEAD"], cwd=repo_dir)
    run(["git", "clean", "-fd"], cwd=repo_dir)
    run(["git", "fetch", "origin", "main"], cwd=repo_dir)
    run(["git", "checkout", "-B", "mirror-publish", "origin/main"], cwd=repo_dir)
    run(["git", "apply", "--index", "--binary", str(patch_path)], cwd=repo_dir)
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_dir, check=False)
    if staged.returncode == 0:
        raise AssertionError("Patch did not stage any changes.")
    run(["git", "commit", "-m", "chore(mirror): update managed mirrors"], cwd=repo_dir)
    run(["git", "push", "origin", "HEAD:main"], cwd=repo_dir)
    return run(["git", "rev-parse", "HEAD"], cwd=repo_dir)


class MirrorUpdateWorkflowPathTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.origin_dir = self.root / "origin.git"
        self.work_dir = self.root / "work"

        subprocess.run(["git", "init", "--bare", str(self.origin_dir)], check=True, capture_output=True, text=True)
        subprocess.run(["git", "clone", str(self.origin_dir), str(self.work_dir)], check=True, capture_output=True, text=True)
        run(["git", "config", "user.name", "Tester"], cwd=self.work_dir)
        run(["git", "config", "user.email", "tester@example.com"], cwd=self.work_dir)
        run(["git", "checkout", "-b", "main"], cwd=self.work_dir)
        (self.work_dir / "docs").mkdir()
        (self.work_dir / "docs" / "Mirrors.md").write_text("initial\n", encoding="utf-8")
        run(["git", "add", "docs/Mirrors.md"], cwd=self.work_dir)
        run(["git", "commit", "-m", "init"], cwd=self.work_dir)
        run(["git", "push", "origin", "HEAD:main"], cwd=self.work_dir)
        run(["git", "checkout", "-b", "mirror"], cwd=self.work_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_noop_path_skips_patch_creation(self):
        patch_path = self.root / "mirror-update.patch"
        origin_head_before = run(["git", "rev-parse", "refs/remotes/origin/main"], cwd=self.work_dir)

        changed = run_patch_capture(self.work_dir, patch_path)

        self.assertFalse(changed)
        self.assertFalse(patch_path.exists())
        self.assertEqual(origin_head_before, run(["git", "rev-parse", "refs/remotes/origin/main"], cwd=self.work_dir))

    def test_changed_path_publishes_single_commit_to_main(self):
        patch_path = self.root / "mirror-update.patch"
        (self.work_dir / "docs" / "Mirrors.md").write_text("updated\n", encoding="utf-8")

        changed = run_patch_capture(self.work_dir, patch_path)
        published_sha = run_publish(self.work_dir, patch_path)

        self.assertTrue(changed)
        self.assertTrue(patch_path.exists())

        inspect_dir = self.root / "inspect"
        subprocess.run(["git", "clone", str(self.origin_dir), str(inspect_dir)], check=True, capture_output=True, text=True)
        run(["git", "checkout", "main"], cwd=inspect_dir)
        self.assertEqual((inspect_dir / "docs" / "Mirrors.md").read_text(encoding="utf-8"), "updated\n")
        self.assertEqual(run(["git", "log", "--format=%s", "-1"], cwd=inspect_dir), "chore(mirror): update managed mirrors")
        self.assertEqual(run(["git", "rev-parse", "HEAD"], cwd=inspect_dir), published_sha)
        self.assertEqual(run(["git", "rev-list", "--count", "main"], cwd=inspect_dir), "2")
        shutil.rmtree(inspect_dir)


if __name__ == "__main__":
    unittest.main()
