from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import importlib

import tasks  # noqa: E402


class GithubMirrorPreserveExistingDocTests(unittest.TestCase):
    """A failed GitHub releases fetch must never blank/overwrite a good doc."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        # CWD is a runner dir one level below root, so the function's
        # '../docs/Mirrors' path resolves to <root>/docs/Mirrors.
        self.runner = self.root / "runner"
        self.runner.mkdir()
        self.docs_dir = self.root / "docs" / "Mirrors"
        self.docs_dir.mkdir(parents=True)
        self.filename = "Mirrors-PreserveTest.md"
        self.markdown_path = self.docs_dir / self.filename
        self.good_content = (
            "---\ntitle: PreserveTest\n---\n\n"
            "## v1.0.0\n\n- <GithubMirrorLink />\n\n"
        )
        self.markdown_path.write_text(self.good_content, encoding="utf-8")

    def tearDown(self):
        import shutil

        shutil.rmtree(self.root, ignore_errors=True)

    def _run(self, api_json):
        mirror = {
            "type": "github",
            "softwareName": "PreserveTest",
            "officialSite": "https://github.com/example/preserve-test/",
            "markdownFilename": self.filename,
            "createDate": "2024-01-01",
        }
        response = mock.Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = api_json

        original_cwd = os.getcwd()
        try:
            os.chdir(str(self.runner))
            with mock.patch(
                "tasks.requests.get", return_value=response
            ), mock.patch("tasks.load_description", return_value=" "):
                tasks.create_github_mirror(mirror)
        finally:
            os.chdir(original_cwd)

    def test_rate_limited_api_preserves_existing_doc(self):
        self._run(
            {
                "message": "API rate limit exceeded",
                "documentation_url": "https://docs.github.com",
            }
        )
        self.assertEqual(
            self.markdown_path.read_text(encoding="utf-8"),
            self.good_content,
            "Existing doc must be left untouched when the GitHub API fails",
        )

    def test_empty_release_list_preserves_existing_doc(self):
        self._run([])
        self.assertEqual(
            self.markdown_path.read_text(encoding="utf-8"),
            self.good_content,
            "An empty release list must not blank an existing doc",
        )


if __name__ == "__main__":
    unittest.main()