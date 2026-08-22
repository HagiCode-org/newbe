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
            'metadataOwner': 'metadata',
            'metadataRepo': 'syncer-action',
            'blobPrefix': 'release-sync',
            'expectedVersion': 1,
            'timeoutSeconds': 5,
        }

    def test_reads_root_index_and_draft_manifest_asset(self):
        index = {
            'version': 1,
            'repositories': [{
                'repositoryKey': 'owner/repo',
                'releaseTagName': 'v1',
                'manifestPath': 'release-sync/owner/repo/manifest.json',
                'recordCount': 2,
                'status': 'synced',
                'lastSuccessfulAt': '2026-08-21T00:00:00Z',
                'releases': [{
                    'repositoryKey': 'owner/repo',
                    'releaseTagName': 'v1',
                    'manifestPath': 'release-sync/owner/repo/manifest.json',
                    'recordCount': 2,
                    'status': 'synced',
                    'lastSuccessfulAt': '2026-08-21T00:00:00Z',
                }],
            }],
        }
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
        responses = [
            Response([{'id': 1, 'draft': True, 'created_at': '2026-08-21'}]),
            Response([
                {'name': 'release-sync__index.json', 'url': 'index-url'},
                {'name': 'release-sync__owner__repo__manifest.json', 'url': 'manifest-url'},
            ]),
            Response(index),
            Response(manifest),
        ]
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test-token'}), patch(
            'tools.tasks.requests.get', side_effect=responses
        ):
            records = tasks.fetch_manifest_records(self.source, 'v1')

        self.assertEqual(records[0]['providerKey'], '123pan')
        self.assertEqual(records[0]['shareUrl'], 'https://www.123pan.com/s/example')
        self.assertEqual(len(records), 2)
        self.assertEqual(records[1]['shareUrl'], '')

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


if __name__ == '__main__':
    unittest.main()
