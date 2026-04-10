from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import tasks as mirror_tasks


TOOLS_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = TOOLS_DIR.parent / "docs" / "Mirrors"
DESCRIPTIONS_DIR = TOOLS_DIR / "MirrorDescription"
MIRRORS_DEF_PATH = TOOLS_DIR / "mirrorsDef.json"

A_TIER_EXPECTATIONS = [
    {
        "softwareName": "Azure Data Studio",
        "officialSite": "https://github.com/microsoft/azuredatastudio/",
        "markdownFilename": "Mirrors-Azure-Data-Studio.md",
    },
    {
        "softwareName": "Tabby",
        "officialSite": "https://github.com/Eugeny/tabby/",
        "markdownFilename": "Mirrors-Tabby.md",
    },
    {
        "softwareName": "Motrix",
        "officialSite": "https://github.com/agalwood/Motrix/",
        "markdownFilename": "Mirrors-Motrix.md",
    },
    {
        "softwareName": "MarkText",
        "officialSite": "https://github.com/marktext/marktext/",
        "markdownFilename": "Mirrors-MarkText.md",
    },
    {
        "softwareName": "Electron Fiddle",
        "officialSite": "https://github.com/electron/fiddle/",
        "markdownFilename": "Mirrors-Electron-Fiddle.md",
    },
    {
        "softwareName": "Gitea",
        "officialSite": "https://github.com/go-gitea/gitea/",
        "markdownFilename": "Mirrors-Gitea.md",
    },
    {
        "softwareName": "GitHub Desktop",
        "officialSite": "https://github.com/desktop/desktop/",
        "markdownFilename": "Mirrors-GitHub-Desktop.md",
    },
    {
        "softwareName": "WezTerm",
        "officialSite": "https://github.com/wez/wezterm/",
        "markdownFilename": "Mirrors-WezTerm.md",
    },
    {
        "softwareName": "llama.cpp",
        "officialSite": "https://github.com/ggml-org/llama.cpp/",
        "markdownFilename": "Mirrors-llama-cpp.md",
    },
    {
        "softwareName": "LocalAI",
        "officialSite": "https://github.com/mudler/LocalAI/",
        "markdownFilename": "Mirrors-LocalAI.md",
    },
    {
        "softwareName": "GPT4All",
        "officialSite": "https://github.com/nomic-ai/gpt4all/",
        "markdownFilename": "Mirrors-GPT4All.md",
    },
    {
        "softwareName": "Dive",
        "officialSite": "https://github.com/OpenAgentPlatform/Dive/",
        "markdownFilename": "Mirrors-Dive.md",
    },
    {
        "softwareName": "PowerToys",
        "officialSite": "https://github.com/microsoft/PowerToys/",
        "markdownFilename": "Mirrors-PowerToys.md",
    },
    {
        "softwareName": "PowerShell",
        "officialSite": "https://github.com/PowerShell/PowerShell/",
        "markdownFilename": "Mirrors-PowerShell.md",
    },
]


def load_catalog() -> list[dict[str, object]]:
    with open(MIRRORS_DEF_PATH, encoding="utf-8") as handle:
        return json.load(handle)["mirrors"]


class MirrorTierACatalogTests(unittest.TestCase):
    def test_requested_a_tier_repositories_exist_once_in_catalog(self):
        mirrors = load_catalog()

        for expected in A_TIER_EXPECTATIONS:
            with self.subTest(official_site=expected["officialSite"]):
                matches = [
                    mirror
                    for mirror in mirrors
                    if mirror.get("officialSite") == expected["officialSite"]
                ]
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0]["softwareName"], expected["softwareName"])
                self.assertEqual(matches[0]["markdownFilename"], expected["markdownFilename"])

    def test_requested_a_tier_repositories_have_description_and_generated_page(self):
        for expected in A_TIER_EXPECTATIONS:
            with self.subTest(software_name=expected["softwareName"]):
                description_path = DESCRIPTIONS_DIR / f"{expected['softwareName']}.md"
                page_path = DOCS_DIR / expected["markdownFilename"]

                self.assertTrue(description_path.exists(), description_path)
                self.assertTrue(description_path.read_text(encoding="utf-8").strip())

                self.assertTrue(page_path.exists(), page_path)
                page_text = page_path.read_text(encoding="utf-8")
                self.assertIn(f"title: {expected['softwareName']}", page_text)
                self.assertIn(expected["officialSite"], page_text)


class FakeResponse:
    def __init__(self, *, text: str = "", json_data=None):
        self.text = text
        self._json_data = json_data

    def json(self):
        return self._json_data

    def raise_for_status(self):
        return None


class GitHubHtmlFallbackTests(unittest.TestCase):
    def test_create_github_mirror_generates_new_page_from_html_fallback(self):
        mirror = {
            "type": "github",
            "softwareName": "Example Repo",
            "officialSite": "https://github.com/example-owner/example-repo/",
            "mirrorPrefix": "https://github.abskoop.workers.dev/https://github.com",
            "markdownFilename": "Mirrors-Example-Repo.md",
            "createDate": "2026-04-10",
        }
        api_url = "https://api.github.com/repos/example-owner/example-repo/releases"
        releases_url = "https://github.com/example-owner/example-repo/releases"
        assets_url = "https://github.com/example-owner/example-repo/releases/expanded_assets/v1.2.3"

        releases_page_html = (
            f'<include-fragment loading="lazy" src="{assets_url}" data-view-component="true"></include-fragment>'
        )
        expanded_assets_html = """
<div data-view-component="true" class="Box Box--condensed tmp-mt-3">
  <a href="/example-owner/example-repo/releases/download/v1.2.3/example.zip" rel="nofollow" data-turbo="false" data-view-component="true" class="Truncate">
    <span data-view-component="true" class="Truncate-text text-bold">example.zip</span>
  </a>
</div>
"""

        def fake_get(url, headers=None, timeout=30):
            if url == api_url:
                return FakeResponse(json_data={"message": "rate limited"})
            if url == releases_url:
                return FakeResponse(text=releases_page_html)
            if url == assets_url:
                return FakeResponse(text=expanded_assets_html)
            raise AssertionError(f"Unexpected URL: {url}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            tools_dir = temp_root / "tools"
            description_dir = tools_dir / "MirrorDescription"
            docs_dir = temp_root / "docs" / "Mirrors"

            description_dir.mkdir(parents=True)
            docs_dir.mkdir(parents=True)
            (description_dir / "Example Repo.md").write_text("用于测试 HTML fallback。", encoding="utf-8")

            old_cwd = Path.cwd()
            os.chdir(tools_dir)
            try:
                with patch.object(mirror_tasks.requests, "get", side_effect=fake_get):
                    mirror_tasks.create_github_mirror(mirror)
            finally:
                os.chdir(old_cwd)

            page_text = (docs_dir / "Mirrors-Example-Repo.md").read_text(encoding="utf-8")
            self.assertIn("## v1.2.3", page_text)
            self.assertIn("example.zip", page_text)
            self.assertIn(
                'https://github.com/example-owner/example-repo/releases/download/v1.2.3/example.zip',
                page_text,
            )


if __name__ == "__main__":
    unittest.main()
