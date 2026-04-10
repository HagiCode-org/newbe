from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests

from tools import tasks as mirror_tasks

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
CONTAINER_SAS_ENV = "AZURE_STORAGE_BLOB_SAS_URL"
CONTAINER_SAS_URL = "https://example.blob.core.windows.net/release-sync?sv=test&sp=rl&sig=example"


def build_manifest_source():
    return {
        "repositoryKey": "ollama/ollama",
        "source": "azure",
        "expectedVersion": 1,
        "containerSasUrlEnv": CONTAINER_SAS_ENV,
        "blobPrefix": "release-sync",
        "timeoutSeconds": 15,
    }


def build_manifest_url(release_tag_name: str) -> str:
    return (
        "https://example.blob.core.windows.net/"
        f"release-sync/release-sync/ollama/ollama/{release_tag_name}/manifest.json"
        "?sv=test&sp=rl&sig=example"
    )


class FakeResponse:
    def __init__(self, *, json_data=None, status_code=200, json_error=None):
        self._json_data = json_data
        self.status_code = status_code
        self._json_error = json_error

    def json(self):
        if self._json_error is not None:
            raise self._json_error
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def build_manifest_payload(records):
    return {
        "repositoryKey": "ollama/ollama",
        "version": 1,
        "updatedAt": "2026-04-10T12:30:00Z",
        "records": records,
    }


class ManifestFetchTests(unittest.TestCase):
    def setUp(self):
        mirror_tasks.MANIFEST_RECORD_CACHE.clear()

    def test_fetch_manifest_records_normalizes_entries_and_uses_cache(self):
        manifest_source = build_manifest_source()
        payload = build_manifest_payload([
            {
                "repositoryKey": "ollama/ollama",
                "releaseTagName": "v0.20.2",
                "assetName": "OllamaSetup.exe",
                "providerName": "123pan",
                "shareUrl": "https://www.123pan.com/s/example-share",
                "status": "synced",
                "lastSyncedAt": "2026-04-10T12:00:00Z",
            }
        ])
        calls = []

        def fake_get(url, headers=None, timeout=15):
            calls.append((url, timeout))
            return FakeResponse(json_data=payload)

        with patch.dict(os.environ, {CONTAINER_SAS_ENV: CONTAINER_SAS_URL}, clear=False):
            with patch.object(mirror_tasks.requests, "get", side_effect=fake_get):
                first = mirror_tasks.fetch_manifest_records(manifest_source, "v0.20.2")
                second = mirror_tasks.fetch_manifest_records(manifest_source, "v0.20.2")

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], build_manifest_url("v0.20.2"))
        self.assertEqual(first, second)
        self.assertEqual(first[0]["providerKey"], "123pan")
        self.assertEqual(first[0]["displayName"], "123pan")
        self.assertEqual(first[0]["shareUrl"], "https://www.123pan.com/s/example-share")
        self.assertEqual(first[0]["source"], "azure")

    def test_fetch_manifest_records_degrades_on_request_failure(self):
        manifest_source = build_manifest_source()

        with patch.dict(os.environ, {CONTAINER_SAS_ENV: CONTAINER_SAS_URL}, clear=False):
            with patch.object(mirror_tasks.requests, "get", side_effect=requests.Timeout("timed out")):
                records = mirror_tasks.fetch_manifest_records(manifest_source, "v0.20.2")

        self.assertEqual(records, [])

    def test_fetch_manifest_records_degrades_on_non_200_response(self):
        manifest_source = build_manifest_source()

        with patch.dict(os.environ, {CONTAINER_SAS_ENV: CONTAINER_SAS_URL}, clear=False):
            with patch.object(
                mirror_tasks.requests,
                "get",
                return_value=FakeResponse(status_code=503, json_data={"message": "unavailable"}),
            ):
                records = mirror_tasks.fetch_manifest_records(manifest_source, "v0.20.2")

        self.assertEqual(records, [])

    def test_fetch_manifest_records_degrades_on_invalid_json(self):
        manifest_source = build_manifest_source()
        invalid_json_error = json.JSONDecodeError("invalid", "{", 1)

        with patch.dict(os.environ, {CONTAINER_SAS_ENV: CONTAINER_SAS_URL}, clear=False):
            with patch.object(
                mirror_tasks.requests,
                "get",
                return_value=FakeResponse(json_error=invalid_json_error),
            ):
                records = mirror_tasks.fetch_manifest_records(manifest_source, "v0.20.2")

        self.assertEqual(records, [])

    def test_fetch_manifest_records_returns_empty_when_container_sas_env_is_missing(self):
        manifest_source = build_manifest_source()

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(mirror_tasks.requests, "get") as get_mock:
                records = mirror_tasks.fetch_manifest_records(manifest_source, "v0.20.2")

        self.assertEqual(records, [])
        get_mock.assert_not_called()

    def test_fetch_manifest_records_returns_empty_for_repository_without_manifest_source(self):
        self.assertEqual(mirror_tasks.fetch_manifest_records(None, "v0.20.2"), [])


class OllamaMirrorGenerationTests(unittest.TestCase):
    def setUp(self):
        mirror_tasks.MANIFEST_RECORD_CACHE.clear()

    def test_create_github_mirror_embeds_exact_asset_provider_links_and_keeps_fallback_assets(self):
        mirror = {
            "type": "github",
            "softwareName": "ollama",
            "officialSite": "https://github.com/ollama/ollama/",
            "mirrorPrefix": "https://github.abskoop.workers.dev/https://github.com",
            "repositoryKey": "ollama/ollama",
            "preferredProviders": ["123pan"],
            "manifestSource": build_manifest_source(),
            "markdownFilename": "Mirrors-ollama.md",
            "createDate": "2026-04-10",
        }
        github_api_url = "https://api.github.com/repos/ollama/ollama/releases"
        manifest_url = build_manifest_url("v0.20.2")
        releases_payload = [
            {
                "tag_name": "v0.20.2",
                "published_at": "2026-04-10T12:30:00Z",
                "assets": [
                    {
                        "browser_download_url": "https://github.com/ollama/ollama/releases/download/v0.20.2/OllamaSetup.exe",
                        "name": "OllamaSetup.exe",
                    },
                    {
                        "browser_download_url": "https://github.com/ollama/ollama/releases/download/v0.20.2/install.sh",
                        "name": "install.sh",
                    },
                ],
            }
        ]
        manifest_payload = json.loads(
            (FIXTURES_DIR / "ollama-azure-manifest.json").read_text(encoding="utf-8")
        )

        def fake_get(url, headers=None, timeout=30):
            if url == github_api_url:
                return FakeResponse(json_data=releases_payload)
            if url == manifest_url:
                return FakeResponse(json_data=manifest_payload)
            raise AssertionError(f"Unexpected URL: {url}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            tools_dir = temp_root / "tools"
            description_dir = tools_dir / "MirrorDescription"
            docs_dir = temp_root / "docs" / "Mirrors"

            description_dir.mkdir(parents=True)
            docs_dir.mkdir(parents=True)
            (description_dir / "ollama.md").write_text("用于测试 Ollama 123pan manifest。", encoding="utf-8")

            old_cwd = Path.cwd()
            os.chdir(tools_dir)
            try:
                with patch.dict(os.environ, {CONTAINER_SAS_ENV: CONTAINER_SAS_URL}, clear=False):
                    with patch.object(mirror_tasks.requests, "get", side_effect=fake_get):
                        mirror_tasks.create_github_mirror(mirror)
            finally:
                os.chdir(old_cwd)

            page_text = (docs_dir / "Mirrors-ollama.md").read_text(encoding="utf-8")

        self.assertIn('preferredProviders={["123pan"]}', page_text)
        self.assertIn('resolvedMirrors={[{"providerKey": "123pan"', page_text)
        self.assertIn('https://www.123pan.com/s/example-share', page_text)

        install_line = next(
            line for line in page_text.splitlines()
            if 'text="install.sh"' in line
        )
        self.assertNotIn('resolvedMirrors=', install_line)
        self.assertIn('repositoryKey="ollama/ollama"', install_line)

    def test_create_github_mirror_keeps_provider_contract_generic_for_future_mirrors(self):
        mirror = {
            "type": "github",
            "softwareName": "ollama",
            "officialSite": "https://github.com/ollama/ollama/",
            "mirrorPrefix": "https://github.abskoop.workers.dev/https://github.com",
            "repositoryKey": "ollama/ollama",
            "preferredProviders": ["123pan"],
            "manifestSource": build_manifest_source(),
            "markdownFilename": "Mirrors-ollama.md",
            "createDate": "2026-04-10",
        }
        github_api_url = "https://api.github.com/repos/ollama/ollama/releases"
        manifest_url = build_manifest_url("v0.20.2")
        releases_payload = [
            {
                "tag_name": "v0.20.2",
                "published_at": "2026-04-10T12:30:00Z",
                "assets": [
                    {
                        "browser_download_url": "https://github.com/ollama/ollama/releases/download/v0.20.2/OllamaSetup.exe",
                        "name": "OllamaSetup.exe",
                    },
                ],
            }
        ]
        manifest_payload = build_manifest_payload([
            {
                "repositoryKey": "ollama/ollama",
                "releaseTagName": "v0.20.2",
                "assetName": "OllamaSetup.exe",
                "providerName": "123pan",
                "shareUrl": "https://www.123pan.com/s/example-share",
                "status": "synced",
                "lastSyncedAt": "2026-04-10T12:00:00Z",
            },
            {
                "repositoryKey": "ollama/ollama",
                "releaseTagName": "v0.20.2",
                "assetName": "OllamaSetup.exe",
                "providerName": "future-drive",
                "shareUrl": "https://future.example.com/ollama-setup",
                "status": "synced",
                "lastSyncedAt": "2026-04-10T12:01:00Z",
            },
        ])

        def fake_get(url, headers=None, timeout=30):
            if url == github_api_url:
                return FakeResponse(json_data=releases_payload)
            if url == manifest_url:
                return FakeResponse(json_data=manifest_payload)
            raise AssertionError(f"Unexpected URL: {url}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            tools_dir = temp_root / "tools"
            description_dir = tools_dir / "MirrorDescription"
            docs_dir = temp_root / "docs" / "Mirrors"

            description_dir.mkdir(parents=True)
            docs_dir.mkdir(parents=True)
            (description_dir / "ollama.md").write_text("用于测试 future provider。", encoding="utf-8")

            old_cwd = Path.cwd()
            os.chdir(tools_dir)
            try:
                with patch.dict(os.environ, {CONTAINER_SAS_ENV: CONTAINER_SAS_URL}, clear=False):
                    with patch.object(mirror_tasks.requests, "get", side_effect=fake_get):
                        mirror_tasks.create_github_mirror(mirror)
            finally:
                os.chdir(old_cwd)

            page_text = (docs_dir / "Mirrors-ollama.md").read_text(encoding="utf-8")

        self.assertIn('"providerKey": "123pan"', page_text)
        self.assertIn('"providerKey": "future-drive"', page_text)
        self.assertIn('preferredProviders={["123pan"]}', page_text)


if __name__ == "__main__":
    unittest.main()
