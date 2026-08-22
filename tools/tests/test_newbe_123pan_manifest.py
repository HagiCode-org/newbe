import os
import unittest
from unittest.mock import patch

from tools import tasks
from tools.mirror.github import get_github_version_section


class Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class Newbe123PanManifestTests(unittest.TestCase):
    def setUp(self):
        tasks.ROOT_MANIFEST_INDEX_CACHE.clear()
        tasks.MANIFEST_RECORD_CACHE.clear()
        self.source = {
            'repositoryKey': 'owner/repo',
            'baseUrl': 'https://syncer.hagicode.com',
            'indexPath': 'release-sync/index.json',
            'manifestVersion': 1,
            'timeoutSeconds': 5,
        }

    def test_reads_root_index_and_draft_manifest_asset(self):
        index = {'repositories': [{
            'repositoryKey': 'owner/repo',
            'releases': [{
                'releaseTagName': 'v1',
                'manifestPath': 'manifests/v1.json',
                'recordCount': 2,
                'status': 'synced',
                'lastSuccessfulAt': '2026-08-21T00:00:00Z',
            }],
        }]}
        manifest = {
            'version': 1,
            'records': [{
                'repositoryKey': 'owner/repo',
                'releaseTagName': 'v1',
                'assetName': 'app.zip',
                'providerName': ' PAN123 ',
                'shareUrl': ' https://www.123pan.com/s/example ',
                'status': 'synced',
                'lastSyncedAt': '2026-08-21T00:00:00Z',
            }, {
                'repositoryKey': 'owner/repo',
                'releaseTagName': 'v1',
                'assetName': 'app.zip',
                'providerName': '123pan',
                'shareUrl': ' ',
                'status': 'synced',
            }],
        }
        with patch('tools.tasks.requests.get', side_effect=[Response(index), Response(manifest)]):
            records = tasks.fetch_manifest_records(self.source, 'v1')

        self.assertEqual(records[0]['providerKey'], '123pan')
        self.assertEqual(records[0]['shareUrl'], 'https://www.123pan.com/s/example')
        self.assertEqual(len(records), 1)

    def test_mirror_section_keeps_direct_link_without_preferred_list(self):
        output = get_github_version_section(
            {'tag_name': 'v1', 'assets': [{
                'name': 'app.zip',
                'browser_download_url': 'https://github.com/owner/repo/releases/download/v1/app.zip',
            }]},
            resolved_mirrors_by_asset={'app.zip': [{
                'providerKey': '123pan',
                'shareUrl': 'https://www.123pan.com/s/example',
                'displayName': '123pan',
                'source': 'syncer-action',
                'status': 'synced',
                'syncedAt': '2026-08-21T00:00:00Z',
            }]},
        )
        self.assertIn('https://www.123pan.com/s/example', output)
        self.assertNotIn('releases/download', output.split('resolvedMirrors=', 1)[1])

    def test_normalize_manifest_records_preserves_paid_share_url_variants(self):
        records = tasks.normalize_manifest_records({
            'version': 1,
            'records': [
                {
                    'repositoryKey': 'owner/repo',
                    'releaseTagName': 'v1',
                    'assetName': 'with-paid.zip',
                    'providerName': '123pan',
                    'shareUrl': 'https://example.test/original',
                    'paidShareUrl': ' https://example.test/paid ',
                    'status': 'synced',
                },
                {
                    'repositoryKey': 'owner/repo',
                    'releaseTagName': 'v1',
                    'assetName': 'missing-paid.zip',
                    'providerName': '123pan',
                    'shareUrl': 'https://example.test/missing',
                    'status': 'synced',
                },
                {
                    'repositoryKey': 'owner/repo',
                    'releaseTagName': 'v1',
                    'assetName': 'empty-paid.zip',
                    'providerName': '123pan',
                    'shareUrl': 'https://example.test/empty',
                    'paidShareUrl': ' ',
                    'status': 'synced',
                },
            ],
        }, self.source)

        self.assertEqual(records[0]['paidShareUrl'], 'https://example.test/paid')
        self.assertIsNone(records[1]['paidShareUrl'])
        self.assertIsNone(records[2]['paidShareUrl'])

    def test_mirror_section_uses_paid_link_only_for_latest_release(self):
        release = {'tag_name': 'v1', 'assets': [{
            'name': 'app.zip',
            'browser_download_url': 'https://github.com/owner/repo/releases/download/v1/app.zip',
        }]}
        record = {
            'providerKey': '123pan',
            'shareUrl': 'https://www.123pan.com/s/original',
            'paidShareUrl': 'https://www.123pan.com/s/paid',
            'displayName': '123pan',
            'source': 'syncer-action',
            'status': 'synced',
            'syncedAt': '2026-08-21T00:00:00Z',
        }

        latest_output = get_github_version_section(
            release, resolved_mirrors_by_asset={'app.zip': [record]}, is_latest=True,
        )
        historical_output = get_github_version_section(
            release, resolved_mirrors_by_asset={'app.zip': [record]}, is_latest=False,
        )

        self.assertIn('https://www.123pan.com/s/paid', latest_output)
        self.assertIn('https://www.123pan.com/s/original', historical_output)
        self.assertIn('"fullUrl": "https://www.123pan.com/s/original"', historical_output)
        self.assertIn('"isLatest": false', historical_output)


if __name__ == '__main__':
    unittest.main()
