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


def load_fixture(name: str):
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def build_manifest_source(repository_key: str):
    return {
        "repositoryKey": repository_key,
        "source": "azure",
        "expectedVersion": 1,
        "containerSasUrlEnv": CONTAINER_SAS_ENV,
        "blobPrefix": "release-sync",
        "timeoutSeconds": 15,
    }


def build_manifest_url(repository_key: str, release_tag_name: str) -> str:
    owner, repo = repository_key.split("/", 1)
    return (
        "https://example.blob.core.windows.net/"
        f"release-sync/release-sync/{owner}/{repo}/{release_tag_name}/manifest.json"
        "?sv=test&sp=rl&sig=example"
    )


def build_manifest_payload(repository_key: str, records):
    return {
        "repositoryKey": repository_key,
        "version": 1,
        "updatedAt": "2026-04-10T12:30:00Z",
        "records": records,
    }


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


class ManifestFetchTests(unittest.TestCase):
    def setUp(self):
        mirror_tasks.MANIFEST_RECORD_CACHE.clear()

    def test_fetch_manifest_records_normalizes_entries_and_uses_cache_for_non_ollama_repo(self):
        repository_key = "microsoft/PowerToys"
        manifest_source = build_manifest_source(repository_key)
        payload = load_fixture("powertoys-azure-manifest.json")
        calls = []

        def fake_get(url, headers=None, timeout=15):
            calls.append((url, timeout))
            return FakeResponse(json_data=payload)

        with patch.dict(os.environ, {CONTAINER_SAS_ENV: CONTAINER_SAS_URL}, clear=False):
            with patch.object(mirror_tasks.requests, "get", side_effect=fake_get):
                first = mirror_tasks.fetch_manifest_records(manifest_source, "v0.92.1")
                second = mirror_tasks.fetch_manifest_records(manifest_source, "v0.92.1")

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], build_manifest_url(repository_key, "v0.92.1"))
        self.assertEqual(first, second)

        matching_record = next(
            record
            for record in first
            if record["repositoryKey"] == repository_key
            and record["releaseTagName"] == "v0.92.1"
            and record["assetName"] == "PowerToysUserSetup-0.92.1-x64.exe"
        )
        self.assertEqual(matching_record["providerKey"], "123pan")
        self.assertEqual(matching_record["displayName"], "123pan")
        self.assertEqual(matching_record["shareUrl"], "https://www.123pan.com/s/powertoys-share")
        self.assertEqual(matching_record["source"], "azure")

    def test_fetch_manifest_records_degrades_on_request_failure(self):
        manifest_source = build_manifest_source("microsoft/PowerToys")

        with patch.dict(os.environ, {CONTAINER_SAS_ENV: CONTAINER_SAS_URL}, clear=False):
            with patch.object(mirror_tasks.requests, "get", side_effect=requests.Timeout("timed out")):
                records = mirror_tasks.fetch_manifest_records(manifest_source, "v0.92.1")

        self.assertEqual(records, [])

    def test_fetch_manifest_records_degrades_on_non_200_response(self):
        manifest_source = build_manifest_source("microsoft/PowerToys")

        with patch.dict(os.environ, {CONTAINER_SAS_ENV: CONTAINER_SAS_URL}, clear=False):
            with patch.object(
                mirror_tasks.requests,
                "get",
                return_value=FakeResponse(status_code=503, json_data={"message": "unavailable"}),
            ):
                records = mirror_tasks.fetch_manifest_records(manifest_source, "v0.92.1")

        self.assertEqual(records, [])

    def test_fetch_manifest_records_degrades_on_invalid_json(self):
        manifest_source = build_manifest_source("microsoft/PowerToys")
        invalid_json_error = json.JSONDecodeError("invalid", "{", 1)

        with patch.dict(os.environ, {CONTAINER_SAS_ENV: CONTAINER_SAS_URL}, clear=False):
            with patch.object(
                mirror_tasks.requests,
                "get",
                return_value=FakeResponse(json_error=invalid_json_error),
            ):
                records = mirror_tasks.fetch_manifest_records(manifest_source, "v0.92.1")

        self.assertEqual(records, [])

    def test_fetch_manifest_records_degrades_on_invalid_payload_shape(self):
        manifest_source = build_manifest_source("microsoft/PowerToys")
        invalid_payload = load_fixture("invalid-azure-manifest.json")

        with patch.dict(os.environ, {CONTAINER_SAS_ENV: CONTAINER_SAS_URL}, clear=False):
            with patch.object(
                mirror_tasks.requests,
                "get",
                return_value=FakeResponse(json_data=invalid_payload),
            ):
                records = mirror_tasks.fetch_manifest_records(manifest_source, "v0.92.1")

        self.assertEqual(records, [])

    def test_fetch_manifest_records_returns_empty_when_container_sas_env_is_missing(self):
        manifest_source = build_manifest_source("microsoft/PowerToys")

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(mirror_tasks.requests, "get") as get_mock:
                records = mirror_tasks.fetch_manifest_records(manifest_source, "v0.92.1")

        self.assertEqual(records, [])
        get_mock.assert_not_called()

    def test_fetch_manifest_records_returns_empty_for_repository_without_manifest_source(self):
        self.assertEqual(mirror_tasks.fetch_manifest_records(None, "v0.92.1"), [])


class SharedMirrorContractTests(unittest.TestCase):
    def setUp(self):
        mirror_tasks.MANIFEST_RECORD_CACHE.clear()

    def build_powertoys_mirror(self):
        return {
            "type": "github",
            "softwareName": "PowerToys",
            "officialSite": "https://github.com/microsoft/PowerToys/",
            "mirrorPrefix": "https://github.abskoop.workers.dev/https://github.com",
            "repositoryKey": "microsoft/PowerToys",
            "preferredProviders": ["123pan"],
            "manifestSource": build_manifest_source("microsoft/PowerToys"),
            "markdownFilename": "Mirrors-PowerToys.md",
            "createDate": "2026-04-10",
        }

    def render_temp_mirror_page(self, mirror, releases_payload, manifest_payload):
        github_api_url = (
            f"https://api.github.com/repos/"
            f"{mirror['repositoryKey'].split('/', 1)[0]}/{mirror['repositoryKey'].split('/', 1)[1]}/releases"
        )
        manifest_url = build_manifest_url(mirror["repositoryKey"], releases_payload[0]["tag_name"])

        def fake_get(url, headers=None, timeout=None):
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
            (description_dir / f"{mirror['softwareName']}.md").write_text(
                "用于测试共享 manifest 合同。",
                encoding="utf-8",
            )

            old_cwd = Path.cwd()
            os.chdir(tools_dir)
            try:
                with patch.dict(os.environ, {CONTAINER_SAS_ENV: CONTAINER_SAS_URL}, clear=False):
                    with patch.object(mirror_tasks.requests, "get", side_effect=fake_get):
                        mirror_tasks.create_github_mirror(mirror)
            finally:
                os.chdir(old_cwd)

            return (docs_dir / mirror["markdownFilename"]).read_text(encoding="utf-8")

    def test_build_provider_links_by_asset_matches_repository_release_and_asset_exactly(self):
        mirror = self.build_powertoys_mirror()
        release = load_fixture("powertoys-releases.json")[0]
        manifest_records = mirror_tasks.normalize_manifest_records(
            load_fixture("powertoys-azure-manifest.json"),
            build_manifest_source("microsoft/PowerToys"),
        )

        provider_links_by_asset = mirror_tasks.build_provider_links_by_asset(
            release,
            mirror,
            manifest_records,
        )

        self.assertEqual(
            provider_links_by_asset["PowerToysUserSetup-0.92.1-x64.exe"][0]["fullUrl"],
            "https://www.123pan.com/s/powertoys-share",
        )
        self.assertNotIn("PowerToysSetup-0.92.1-arm64.exe", provider_links_by_asset)
        self.assertEqual(set(provider_links_by_asset.keys()), {"PowerToysUserSetup-0.92.1-x64.exe"})

    def test_create_github_mirror_embeds_exact_asset_provider_links_and_keeps_fallback_assets(self):
        mirror = self.build_powertoys_mirror()
        releases_payload = load_fixture("powertoys-releases.json")
        manifest_payload = load_fixture("powertoys-azure-manifest.json")

        page_text = self.render_temp_mirror_page(mirror, releases_payload, manifest_payload)

        self.assertIn('preferredProviders={["123pan"]}', page_text)
        self.assertIn('resolvedMirrors={[{"providerKey": "123pan"', page_text)
        self.assertIn('https://www.123pan.com/s/powertoys-share', page_text)

        setup_line = next(
            line for line in page_text.splitlines()
            if 'text="PowerToysUserSetup-0.92.1-x64.exe"' in line
        )
        other_asset_line = next(
            line for line in page_text.splitlines()
            if 'text="PowerToysSetup-0.92.1-arm64.exe"' in line
        )
        self.assertIn('repositoryKey="microsoft/PowerToys"', setup_line)
        self.assertIn('resolvedMirrors=', setup_line)
        self.assertNotIn('resolvedMirrors=', other_asset_line)
        self.assertIn('repositoryKey="microsoft/PowerToys"', other_asset_line)

    def test_create_github_mirror_keeps_provider_contract_generic_for_future_mirrors(self):
        mirror = self.build_powertoys_mirror()
        releases_payload = load_fixture("powertoys-releases.json")
        manifest_payload = build_manifest_payload(
            "microsoft/PowerToys",
            [
                {
                    "repositoryKey": "microsoft/PowerToys",
                    "releaseTagName": "v0.92.1",
                    "assetName": "PowerToysUserSetup-0.92.1-x64.exe",
                    "providerName": "123pan",
                    "shareUrl": "https://www.123pan.com/s/powertoys-share",
                    "status": "synced",
                    "lastSyncedAt": "2026-04-10T12:00:00Z",
                },
                {
                    "repositoryKey": "microsoft/PowerToys",
                    "releaseTagName": "v0.92.1",
                    "assetName": "PowerToysUserSetup-0.92.1-x64.exe",
                    "providerName": "future-drive",
                    "shareUrl": "https://future.example.com/powertoys-setup",
                    "status": "synced",
                    "lastSyncedAt": "2026-04-10T12:01:00Z",
                },
            ],
        )

        page_text = self.render_temp_mirror_page(mirror, releases_payload, manifest_payload)

        self.assertIn('"providerKey": "123pan"', page_text)
        self.assertIn('"providerKey": "future-drive"', page_text)
        self.assertIn('preferredProviders={["123pan"]}', page_text)


if __name__ == "__main__":
    unittest.main()
