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
            'manifestSource': {
                'repositoryKey': 'owner/repo',
                'baseUrl': 'https://syncer.hagicode.com',
                'indexPath': 'r2/index.json',
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

    def test_unavailable_source_returns_errors_not_empty(self):
        with patch('tools.tasks.requests.get', side_effect=__import__('requests').RequestException('boom')):
            payload, errors = tasks.build_123pan_snapshot(MIRRORS_DEF)

        self.assertTrue(errors)
        self.assertIn('boom', errors[0])


if __name__ == '__main__':
    unittest.main()