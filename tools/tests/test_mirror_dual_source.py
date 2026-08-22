from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SNAPSHOT_PATH = Path("tools") / "123pan-sync-state.json"


def run(cmd: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def write_snapshot(repo_dir: Path, records: dict) -> None:
    payload = {
        "generatedAt": "2026-08-22T00:00:00+00:00",
        "recordCount": len(records),
        "records": dict(sorted(records.items())),
        "errors": [],
    }
    snapshot_file = repo_dir / SNAPSHOT_PATH
    snapshot_file.parent.mkdir(parents=True, exist_ok=True)
    snapshot_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def snapshot_changed(repo_dir: Path, baseline_path: Path) -> bool:
    current = repo_dir / SNAPSHOT_PATH
    if not current.exists():
        # 123pan snapshot generation failed/unavailable: no new state to compare.
        return False
    diff = subprocess.run(
        ["git", "diff", "--quiet", "--no-index", str(baseline_path), str(current)],
        check=False,
    )
    return diff.returncode != 0


def combined_changed(source_changed: bool, pan123_changed: bool) -> bool:
    return source_changed or pan123_changed


def change_source(source_changed: bool, pan123_changed: bool) -> str:
    if source_changed and pan123_changed:
        return "source+123pan"
    if source_changed:
        return "source"
    if pan123_changed:
        return "123pan"
    return "none"


class DualSourceChangeDecisionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.work_dir = self.root / "work"
        self.baseline_path = self.root / "123pan-baseline.json"

        subprocess.run(["git", "init", "--bare", str(self.root / "origin.git")], check=True, capture_output=True, text=True)
        subprocess.run(["git", "clone", str(self.root / "origin.git"), str(self.work_dir)], check=True, capture_output=True, text=True)
        run(["git", "config", "user.name", "Tester"], cwd=self.work_dir)
        run(["git", "config", "user.email", "tester@example.com"], cwd=self.work_dir)
        run(["git", "checkout", "-b", "main"], cwd=self.work_dir)
        (self.work_dir / "docs").mkdir()
        (self.work_dir / "docs" / "Mirrors.md").write_text("initial\n", encoding="utf-8")
        write_snapshot(self.work_dir, {"owner/repo:v1:app.zip": {"syncedAt": "2026-08-21T00:00:00Z", "shareUrl": "https://www.123pan.com/s/example", "status": "synced"}})
        run(["git", "add", "-A"], cwd=self.work_dir)
        run(["git", "commit", "-m", "init"], cwd=self.work_dir)
        run(["git", "push", "origin", "HEAD:main"], cwd=self.work_dir)
        run(["git", "checkout", "-b", "mirror"], cwd=self.work_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _source_changed(self) -> bool:
        run(["git", "add", "-N", "."], cwd=self.work_dir)
        diff = subprocess.run(
            ["git", "diff", "--quiet", "--", ".", f":(exclude){SNAPSHOT_PATH.as_posix()}"],
            cwd=self.work_dir,
            check=False,
        )
        return diff.returncode != 0

    def _pan123_changed(self) -> bool:
        # Baseline = the snapshot committed at the start of the run (HEAD).
        baseline_text = subprocess.run(
            ["git", "show", f"HEAD:{SNAPSHOT_PATH.as_posix()}"],
            cwd=self.work_dir,
            check=True,
            text=True,
            capture_output=True,
        ).stdout
        self.baseline_path.write_text(baseline_text, encoding="utf-8")
        return snapshot_changed(self.work_dir, self.baseline_path)

    def test_source_only_change_publishes(self):
        (self.work_dir / "docs" / "Mirrors.md").write_text("updated\n", encoding="utf-8")
        # 123pan snapshot unchanged.
        write_snapshot(self.work_dir, {"owner/repo:v1:app.zip": {"syncedAt": "2026-08-21T00:00:00Z", "shareUrl": "https://www.123pan.com/s/example", "status": "synced"}})

        source_changed = self._source_changed()
        pan123_changed = self._pan123_changed()

        self.assertTrue(source_changed)
        self.assertFalse(pan123_changed)
        self.assertTrue(combined_changed(source_changed, pan123_changed))
        self.assertEqual(change_source(source_changed, pan123_changed), "source")

    def test_123pan_only_change_publishes(self):
        # Source doc unchanged.
        # 123pan snapshot moved to a new syncedAt.
        write_snapshot(self.work_dir, {"owner/repo:v1:app.zip": {"syncedAt": "2026-08-22T00:00:00Z", "shareUrl": "https://www.123pan.com/s/example", "status": "synced"}})

        source_changed = self._source_changed()
        pan123_changed = self._pan123_changed()

        self.assertFalse(source_changed)
        self.assertTrue(pan123_changed)
        self.assertTrue(combined_changed(source_changed, pan123_changed))
        self.assertEqual(change_source(source_changed, pan123_changed), "123pan")

    def test_both_change_publishes_with_combined_label(self):
        (self.work_dir / "docs" / "Mirrors.md").write_text("updated\n", encoding="utf-8")
        write_snapshot(self.work_dir, {"owner/repo:v1:app.zip": {"syncedAt": "2026-08-22T00:00:00Z", "shareUrl": "https://www.123pan.com/s/example", "status": "synced"}})

        source_changed = self._source_changed()
        pan123_changed = self._pan123_changed()

        self.assertTrue(source_changed)
        self.assertTrue(pan123_changed)
        self.assertEqual(change_source(source_changed, pan123_changed), "source+123pan")

    def test_no_change_is_noop(self):
        # Source doc unchanged, 123pan snapshot identical.
        write_snapshot(self.work_dir, {"owner/repo:v1:app.zip": {"syncedAt": "2026-08-21T00:00:00Z", "shareUrl": "https://www.123pan.com/s/example", "status": "synced"}})

        source_changed = self._source_changed()
        pan123_changed = self._pan123_changed()

        self.assertFalse(source_changed)
        self.assertFalse(pan123_changed)
        self.assertFalse(combined_changed(source_changed, pan123_changed))
        self.assertEqual(change_source(source_changed, pan123_changed), "none")

    def test_123pan_unavailable_falls_back_to_source(self):
        # Simulate an unavailable 123pan snapshot: the snapshot generation failed
        # and no snapshot file exists. The workflow treats 123pan_changed as false
        # and must NOT mask the failure as synced.
        snapshot_file = self.work_dir / SNAPSHOT_PATH
        if snapshot_file.exists():
            snapshot_file.unlink()

        pan123_changed = self._pan123_changed()  # baseline missing -> treated as no prior state
        # Workflow contract: when unavailable, 123pan_changed stays false and is not
        # silently counted as synced.
        self.assertFalse(pan123_changed)

        # Source change must still drive a publish even with 123pan unavailable.
        (self.work_dir / "docs" / "Mirrors.md").write_text("updated\n", encoding="utf-8")
        source_changed = self._source_changed()
        self.assertTrue(combined_changed(source_changed, pan123_changed))
        self.assertEqual(change_source(source_changed, pan123_changed), "source")


if __name__ == "__main__":
    unittest.main()