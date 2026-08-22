import json
import tempfile
import unittest
from unittest.mock import patch

from tools import tasks


class Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


MIRRORS_DEF = {
    'mirrors': [
        {
            'softwareName': 'App',
            'repositoryKey': 'owner/repo',
            'manifestSource': {
                'baseUrl': 'https://syncer.hagicode.com',
                'indexPath': 'release-sync/index.json',
                'manifestVersion': 1,
                'timeoutSeconds': 5,
            },
        },
    ],
}

ROOT_INDEX = {'repositories': [{
    'repositoryKey': 'owner/repo',
    'releases': [{
        'releaseTagName': 'v1',
        'manifestPath': 'manifests/v1.json',
        'recordCount': 1,
        'status': 'synced',
        'lastSuccessfulAt': '2026-08-21T00:00:00Z',
    }],
}]}

MANIFEST = {'version': 1, 'records': [{
    'repositoryKey': 'owner/repo',
    'releaseTagName': 'v1',
    'assetName': 'app.zip',
    'providerName': '123pan',
    'shareUrl': 'https://www.123pan.com/s/example',
    'status': 'synced',
    'lastSyncedAt': '2026-08-21T00:00:00Z',
}]}


class Build123PanSnapshotTests(unittest.TestCase):
    def setUp(self):
        tasks.ROOT_MANIFEST_INDEX_CACHE.clear()
        tasks.MANIFEST_RECORD_CACHE.clear()

    def test_writes_keyed_123pan_records(self):
        with patch('tools.tasks.requests.get', side_effect=[Response(ROOT_INDEX), Response(MANIFEST)]):
            payload, errors = tasks.build_123pan_snapshot(MIRRORS_DEF)

        self.assertEqual(errors, [])
        self.assertEqual(payload['recordCount'], 1)
        key = 'owner/repo:v1:app.zip'
        self.assertIn(key, payload['records'])
        self.assertEqual(payload['records'][key]['syncedAt'], '2026-08-21T00:00:00Z')
        self.assertEqual(payload['records'][key]['shareUrl'], 'https://www.123pan.com/s/example')

    def test_non_123pan_records_are_excluded(self):
        other = dict(MANIFEST)
        other['records'] = [
            MANIFEST['records'][0],
            {**MANIFEST['records'][0], 'providerName': 'aliyun', 'shareUrl': 'https://x/y'},
        ]
        with patch('tools.tasks.requests.get', side_effect=[Response(ROOT_INDEX), Response(other)]):
            payload, errors = tasks.build_123pan_snapshot(MIRRORS_DEF)

        self.assertEqual(payload['recordCount'], 1)

    def test_repository_key_resolved_from_mirror(self):
        # Manifest source without repositoryKey must fall back to the mirror's
        # repositoryKey so detection matches the manifest fetched during generation.
        md = {
            'mirrors': [{
                'softwareName': 'App',
                'repositoryKey': 'owner/repo',
                'manifestSource': {
                    'baseUrl': 'https://syncer.hagicode.com',
                    'indexPath': 'release-sync/index.json',
                    'manifestVersion': 1,
                    'timeoutSeconds': 5,
                },
            }],
        }
        with patch('tools.tasks.requests.get', side_effect=[Response(ROOT_INDEX), Response(MANIFEST)]):
            payload, errors = tasks.build_123pan_snapshot(md)
        self.assertEqual(errors, [])
        self.assertIn('owner/repo:v1:app.zip', payload['records'])


class Detect123PanChangesTests(unittest.TestCase):
    def setUp(self):
        tasks.ROOT_MANIFEST_INDEX_CACHE.clear()
        tasks.MANIFEST_RECORD_CACHE.clear()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.baseline = f"{self.temp_dir.name}/123pan-sync-state.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_baseline_missing_treated_as_changed(self):
        with patch('tools.tasks.requests.get', side_effect=[Response(ROOT_INDEX), Response(MANIFEST)]):
            result = tasks.detect_123pan_changes(MIRRORS_DEF, baseline_path=self.baseline)
        self.assertTrue(result['changed'])
        self.assertEqual(result['status'], 'available')
        self.assertIn('baseline missing', result['diagnostic'])

    def test_same_state_is_unchanged(self):
        with patch('tools.tasks.requests.get', side_effect=[Response(ROOT_INDEX), Response(MANIFEST)]):
            tasks.detect_123pan_changes(MIRRORS_DEF, baseline_path=self.baseline)
        tasks.ROOT_MANIFEST_INDEX_CACHE.clear()
        tasks.MANIFEST_RECORD_CACHE.clear()
        with patch('tools.tasks.requests.get', side_effect=[Response(ROOT_INDEX), Response(MANIFEST)]):
            result = tasks.detect_123pan_changes(MIRRORS_DEF, baseline_path=self.baseline)
        self.assertFalse(result['changed'])
        self.assertEqual(result['status'], 'available')

    def test_updated_syncedat_is_changed(self):
        with patch('tools.tasks.requests.get', side_effect=[Response(ROOT_INDEX), Response(MANIFEST)]):
            tasks.detect_123pan_changes(MIRRORS_DEF, baseline_path=self.baseline)
        tasks.ROOT_MANIFEST_INDEX_CACHE.clear()
        tasks.MANIFEST_RECORD_CACHE.clear()
        updated = dict(MANIFEST)
        updated['records'] = [{
            **MANIFEST['records'][0],
            'lastSyncedAt': '2026-08-22T00:00:00Z',
        }]
        with patch('tools.tasks.requests.get', side_effect=[Response(ROOT_INDEX), Response(updated)]):
            result = tasks.detect_123pan_changes(MIRRORS_DEF, baseline_path=self.baseline)
        self.assertTrue(result['changed'])
        self.assertEqual(result['status'], 'available')

    def test_unavailable_source_is_reported_not_masked(self):
        with patch('tools.tasks.requests.get', side_effect=__import__('requests').RequestException('boom')):
            result = tasks.detect_123pan_changes(MIRRORS_DEF, baseline_path=self.baseline)
        self.assertTrue(result['changed'])
        self.assertEqual(result['status'], 'unavailable')
        self.assertIn('unavailable', result['diagnostic'])


if __name__ == '__main__':
    unittest.main()