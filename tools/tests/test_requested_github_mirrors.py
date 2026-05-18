from __future__ import annotations

import json
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = TOOLS_DIR.parent / "docs" / "Mirrors"
DESCRIPTIONS_DIR = TOOLS_DIR / "MirrorDescription"
MIRRORS_DEF_PATH = TOOLS_DIR / "mirrorsDef.json"

REQUESTED_MIRRORS = [
    {
        "softwareName": "DeepSeek-TUI",
        "officialSite": "https://github.com/Hmbown/DeepSeek-TUI/",
        "markdownFilename": "Mirrors-DeepSeek-TUI.md",
    },
    {
        "softwareName": "Hermes Desktop",
        "officialSite": "https://github.com/fathah/hermes-desktop/",
        "markdownFilename": "Mirrors-Hermes-Desktop.md",
    },
    {
        "softwareName": "OpenHuman",
        "officialSite": "https://github.com/tinyhumansai/openhuman/",
        "markdownFilename": "Mirrors-OpenHuman.md",
    },
]


def load_catalog() -> list[dict[str, object]]:
    with open(MIRRORS_DEF_PATH, encoding="utf-8") as handle:
        return json.load(handle)["mirrors"]


class RequestedGitHubMirrorsTests(unittest.TestCase):
    def test_requested_repositories_exist_once_in_catalog(self):
        mirrors = load_catalog()

        for expected in REQUESTED_MIRRORS:
            with self.subTest(official_site=expected["officialSite"]):
                matches = [
                    mirror
                    for mirror in mirrors
                    if mirror.get("officialSite") == expected["officialSite"]
                ]
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0]["softwareName"], expected["softwareName"])
                self.assertEqual(matches[0]["markdownFilename"], expected["markdownFilename"])

    def test_requested_repositories_have_description_and_generated_page(self):
        for expected in REQUESTED_MIRRORS:
            with self.subTest(software_name=expected["softwareName"]):
                description_path = DESCRIPTIONS_DIR / f"{expected['softwareName']}.md"
                page_path = DOCS_DIR / expected["markdownFilename"]

                self.assertTrue(description_path.exists(), description_path)
                self.assertTrue(description_path.read_text(encoding="utf-8").strip())

                self.assertTrue(page_path.exists(), page_path)
                page_text = page_path.read_text(encoding="utf-8")
                self.assertIn(f"title: {expected['softwareName']}", page_text)
                self.assertIn(expected["officialSite"], page_text)


if __name__ == "__main__":
    unittest.main()
