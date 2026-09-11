# -*- coding: UTF-8 -*-

import html
import json
import logging
import os
import re
from datetime import datetime, timezone
from urllib.parse import quote, unquote, urljoin

import requests
try:
    from invoke import task
except ImportError:
    def task(func=None, *args, **kwargs):
        if callable(func) and not args and not kwargs:
            return func

        def decorator(inner):
            return inner

        return decorator

try:
    from mirror.github import get_github_version_section
    from mirror.huawei import (
        get_version_name,
        get_tbody_xml,
        get_version_order,
        get_huawei_version_section,
        get_html_xml,
        get_huawei_version_section_v2,
    )
    from mirror import load_description
except ModuleNotFoundError:
    from tools.mirror.github import get_github_version_section
    from tools.mirror.huawei import (
        get_version_name,
        get_tbody_xml,
        get_version_order,
        get_huawei_version_section,
        get_html_xml,
        get_huawei_version_section_v2,
    )
    from tools.mirror import load_description

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

logger = logging.getLogger()
MIRROR_DEF_JSON_PATH = "mirrorsDef.json"
GITHUB_REQUEST_HEADERS = {
    "User-Agent": "HagiCode-Mirror-Generator/1.0",
}


def github_api_headers():
    """Headers for the GitHub releases API, authenticated when a token exists.

    When GITHUB_TOKEN is provided (e.g. by the mirror-update workflow), the
    request uses the 5000/hr authenticated budget instead of the 60/hr
    unauthenticated one, so a long mirror run no longer trips rate limits and
    falls back to the degraded HTML scrape.
    """
    headers = dict(GITHUB_REQUEST_HEADERS)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers
MANIFEST_REQUEST_HEADERS = {
    "User-Agent": "HagiCode-Mirror-Manifest/1.0",
    "Accept": "application/json",
}
ROOT_MANIFEST_INDEX_CACHE = {}
MANIFEST_RECORD_CACHE = {}
DEFAULT_R2_BASE_URL = 'https://syncer.hagicode.com/'
DEFAULT_R2_INDEX_PATH = 'release-sync/index.json'
HAGICODE_PROMO_IMPORT = "import HagicodeRecommendation from '../../src/components/HagicodeRecommendation';"
HAGICODE_PROMO_BLOCK = "<HagicodeRecommendation layout=\"page\" />"


def remove_hagicode_promo_from_existing_doc(markdown_path):
    with open(markdown_path, 'r', encoding='utf8') as f:
        post = f.read()

    post = post.replace(f"\n{HAGICODE_PROMO_IMPORT}\n", "\n")
    post = post.replace(HAGICODE_PROMO_IMPORT + "\n", "")
    post = post.replace(HAGICODE_PROMO_IMPORT, "")

    post = post.replace(f"\n{HAGICODE_PROMO_BLOCK}\n", "\n")
    post = post.replace(HAGICODE_PROMO_BLOCK + "\n", "")
    post = post.replace(HAGICODE_PROMO_BLOCK, "")
    post = re.sub(r'\n{3,}', '\n\n', post)

    with open(markdown_path, 'w', encoding='utf8') as f:
        f.write(post)

def load_mirrors_def():
    mirrors_def = json.load(open(MIRROR_DEF_JSON_PATH))
    logger.debug(f'mirrors def load: {mirrors_def}')
    # sort by software name
    mirrors_def['mirrors'].sort(key=lambda item: item['softwareName'])
    return mirrors_def


def normalize_provider_key(provider_key):
    if not provider_key:
        return None
    normalized = str(provider_key).strip().lower()
    if normalized in {'pan123', '123 pan', '123-pan', '123_pan'}:
        return '123pan'
    return normalized


def summarize_provider_counts(records):
    provider_counts = {}
    for record in records or []:
        provider_key = record.get('providerKey') or 'unknown'
        provider_counts[provider_key] = provider_counts.get(provider_key, 0) + 1
    return provider_counts


def validate_manifest_source(manifest_source):
    if not manifest_source:
        return None
    repository_key = str(manifest_source.get('repositoryKey') or '').strip().strip('/')
    if not repository_key:
        raise ValueError('manifestSource.repositoryKey is required when manifestSource is configured')
    expected_version = manifest_source.get('manifestVersion', manifest_source.get('expectedVersion'))
    if expected_version is not None and not isinstance(expected_version, int):
        raise ValueError('manifestSource.manifestVersion must be an integer when provided')
    timeout_seconds = manifest_source.get('timeoutSeconds', 15)
    if not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
        raise ValueError('manifestSource.timeoutSeconds must be a positive integer when provided')
    base_url = str(
        manifest_source.get('baseUrl')
        or manifest_source.get('endpoint')
        or DEFAULT_R2_BASE_URL
    ).strip().rstrip('/') + '/'
    index_path = str(manifest_source.get('indexPath', DEFAULT_R2_INDEX_PATH)).strip('/')
    if not index_path:
        raise ValueError('manifestSource.indexPath must not be empty')

    return {
        **manifest_source,
        'repositoryKey': repository_key,
        'manifestVersion': expected_version,
        'timeoutSeconds': timeout_seconds,
        'source': manifest_source.get('source', 'syncer-r2'),
        'baseUrl': base_url,
        'indexPath': index_path,
        'indexUrl': str(manifest_source.get('indexUrl') or '').strip() or None,
    }


def build_root_manifest_index_url(manifest_source):
    return manifest_source.get('indexUrl') or urljoin(manifest_source['baseUrl'], manifest_source['indexPath'])


def build_manifest_url(manifest_source, release_tag_name):
    manifest_path = manifest_source['_manifestPath']
    if manifest_path.startswith(('http://', 'https://')):
        return manifest_path
    return urljoin(manifest_source['baseUrl'], manifest_path)


def manifest_asset_name(manifest_path):
    return str(manifest_path or '').strip().replace('/', '__')


def normalize_root_manifest_release_summary(repository_key, release_summary):
    if not isinstance(release_summary, dict):
        raise ValueError('Root manifest release summary must be an object')

    required_fields = ('releaseTagName', 'recordCount', 'status', 'lastSuccessfulAt')
    missing_fields = [field for field in required_fields if field not in release_summary]
    if missing_fields:
        raise ValueError(
            f"Root manifest release summary for {repository_key} is missing fields: {', '.join(missing_fields)}"
        )

    release_tag_name = str(release_summary.get('releaseTagName') or '').strip()
    if not release_tag_name:
        raise ValueError(f'Root manifest release summary for {repository_key} must provide releaseTagName')

    record_count = release_summary.get('recordCount')
    if isinstance(record_count, bool):
        raise ValueError(f'Root manifest release summary for {repository_key} has invalid recordCount')
    try:
        normalized_record_count = int(record_count)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f'Root manifest release summary for {repository_key} has non-integer recordCount'
        ) from exc

    status = str(release_summary.get('status') or '').strip().lower()
    if not status:
        raise ValueError(f'Root manifest release summary for {repository_key} must provide status')

    last_successful_at = release_summary.get('lastSuccessfulAt')
    normalized_last_successful_at = None
    if last_successful_at is not None:
        normalized_last_successful_at = str(last_successful_at).strip() or None

    last_attempted_at = release_summary.get('lastAttemptedAt')
    normalized_last_attempted_at = None
    if last_attempted_at is not None:
        normalized_last_attempted_at = str(last_attempted_at).strip() or None

    manifest_path = release_summary.get('manifestPath')
    normalized_manifest_path = None
    if manifest_path is not None:
        normalized_manifest_path = str(manifest_path).strip() or None

    return {
        'repositoryKey': repository_key,
        'releaseTagName': release_tag_name,
        'recordCount': normalized_record_count,
        'status': status,
        'lastAttemptedAt': normalized_last_attempted_at,
        'lastSuccessfulAt': normalized_last_successful_at,
        'manifestPath': normalized_manifest_path,
    }


def normalize_root_manifest_repository(repository_entry):
    if not isinstance(repository_entry, dict):
        raise ValueError('Root manifest repository entry must be an object')

    repository_key = str(repository_entry.get('repositoryKey') or '').strip().strip('/')
    if not repository_key:
        raise ValueError('Root manifest repository entry must provide repositoryKey')

    releases = repository_entry.get('releases')
    if not isinstance(releases, list):
        raise ValueError(f'Root manifest repository entry {repository_key} must provide a releases array')

    normalized_releases = []
    release_summaries_by_tag = {}
    for release_summary in releases:
        normalized_release = normalize_root_manifest_release_summary(repository_key, release_summary)
        normalized_releases.append(normalized_release)
        release_summaries_by_tag[normalized_release['releaseTagName'].strip().lower()] = normalized_release

    return {
        'repositoryKey': repository_key,
        'releases': normalized_releases,
        'releaseSummariesByTag': release_summaries_by_tag,
    }


def normalize_root_manifest_index(payload):
    if not isinstance(payload, dict):
        raise ValueError('Root manifest index payload must be an object')

    repositories = payload.get('repositories')
    if not isinstance(repositories, list):
        raise ValueError('Root manifest index payload must provide a repositories array')

    normalized_repositories = []
    repositories_by_key = {}
    for repository_entry in repositories:
        normalized_repository = normalize_root_manifest_repository(repository_entry)
        normalized_repositories.append(normalized_repository)
        repositories_by_key[normalized_repository['repositoryKey']] = normalized_repository

    return {
        'repositories': normalized_repositories,
        'repositoriesByKey': repositories_by_key,
    }


def fetch_root_manifest_index(manifest_source):
    validated_source = validate_manifest_source(manifest_source)
    if not validated_source:
        return {
            'state': 'fallback',
            'reason': 'manifest_source_missing',
            'diagnostic': 'manifestSource is not configured',
        }

    root_index_url = build_root_manifest_index_url(validated_source)
    if not root_index_url:
        diagnostic = (
            f"Manifest container SAS URL is not configured for {validated_source['repositoryKey']}. "
            "Configure GitHub access for syncer-action draft-release metadata to enable manifest discovery."
        )
        return {
            'state': 'fallback',
            'reason': 'container_sas_url_missing',
            'diagnostic': diagnostic,
        }

    if root_index_url in ROOT_MANIFEST_INDEX_CACHE:
        logger.debug(
            "Manifest root index cache hit for %s (%s)",
            validated_source['repositoryKey'],
            root_index_url,
        )
        return ROOT_MANIFEST_INDEX_CACHE[root_index_url]

    logger.debug(
        "Fetching manifest root index for %s from %s",
        validated_source['repositoryKey'],
        root_index_url,
    )

    try:
        request_headers = MANIFEST_REQUEST_HEADERS
        response = requests.get(
            root_index_url,
            headers=request_headers,
            timeout=validated_source['timeoutSeconds'],
        )
        response.raise_for_status()
        payload = response.json()
        releases = payload.get('repositories') if isinstance(payload, dict) else payload
        if not isinstance(releases, list):
            raise ValueError('Metadata releases response must be an array')
        normalized_payload = normalize_root_manifest_index(payload)
        result = {
            'state': 'ready',
            'rootIndexUrl': root_index_url,
            'repositories': normalized_payload['repositories'],
            'repositoriesByKey': normalized_payload['repositoriesByKey'],
        }
        logger.debug(
            "Manifest root index ready for %s: %s repositories discovered",
            validated_source['repositoryKey'],
            len(normalized_payload['repositories']),
        )
    except requests.Timeout:
        result = {
            'state': 'fallback',
            'rootIndexUrl': root_index_url,
            'reason': 'request_timeout',
            'diagnostic': f'Root manifest index request timed out for {validated_source["repositoryKey"]}',
        }
    except requests.RequestException as exc:
        result = {
            'state': 'fallback',
            'rootIndexUrl': root_index_url,
            'reason': 'request_failed',
            'diagnostic': str(exc),
        }
    except json.JSONDecodeError as exc:
        result = {
            'state': 'fallback',
            'rootIndexUrl': root_index_url,
            'reason': 'invalid_json',
            'diagnostic': str(exc),
        }
    except ValueError as exc:
        result = {
            'state': 'fallback',
            'rootIndexUrl': root_index_url,
            'reason': 'invalid_payload',
            'diagnostic': str(exc),
        }

    ROOT_MANIFEST_INDEX_CACHE[root_index_url] = result
    return result


def get_repository_root_manifest_catalog(manifest_source):
    validated_source = validate_manifest_source(manifest_source)
    if not validated_source:
        return {
            'state': 'fallback',
            'reason': 'manifest_source_missing',
            'diagnostic': 'manifestSource is not configured',
            'releaseSummariesByTag': {},
            'candidateReleaseTags': set(),
        }

    root_manifest_index = fetch_root_manifest_index(validated_source)
    if root_manifest_index.get('state') != 'ready':
        logger.info(
            "Manifest r2 index unavailable for %s: %s (%s)",
            validated_source['repositoryKey'],
            root_manifest_index.get('reason', 'root_index_unavailable'),
            root_manifest_index.get('diagnostic'),
        )
        return {
            'state': 'fallback',
            'reason': root_manifest_index.get('reason', 'root_index_unavailable'),
            'diagnostic': root_manifest_index.get('diagnostic'),
            'rootIndexUrl': root_manifest_index.get('rootIndexUrl'),
            'releaseSummariesByTag': {},
            'candidateReleaseTags': set(),
        }

    repository_key = validated_source['repositoryKey']
    repository_catalog = root_manifest_index['repositoriesByKey'].get(repository_key)
    if not repository_catalog:
        logger.info(
            "Manifest r2 index does not include %s",
            repository_key,
        )
        return {
            'state': 'fallback',
            'reason': 'repository_missing',
            'diagnostic': f'Root manifest index does not cover repository {repository_key}',
            'rootIndexUrl': root_manifest_index.get('rootIndexUrl'),
            'releaseSummariesByTag': {},
            'candidateReleaseTags': set(),
        }

    release_summaries_by_tag = repository_catalog['releaseSummariesByTag']
    candidate_release_tags = select_candidate_release_tags(release_summaries_by_tag)
    logger.info(
        "Manifest root index guided mode for %s: %s candidate releases with sync evidence",
        repository_key,
        len(candidate_release_tags),
    )
    return {
        'state': 'guided',
        'reason': 'repository_covered',
        'diagnostic': None,
        'rootIndexUrl': root_manifest_index.get('rootIndexUrl'),
        'repository': repository_catalog,
        'releaseSummariesByTag': release_summaries_by_tag,
        'candidateReleaseTags': candidate_release_tags,
    }


def has_root_manifest_sync_evidence(release_summary):
    if not release_summary:
        return False

    record_count = release_summary.get('recordCount')
    last_successful_at = release_summary.get('lastSuccessfulAt')
    return (
        isinstance(record_count, int)
        and record_count > 0
        and last_successful_at is not None
        and str(last_successful_at).strip() != ''
    )


def select_candidate_release_tags(release_summaries):
    candidate_release_tags = set()
    items = release_summaries.values() if isinstance(release_summaries, dict) else release_summaries
    for release_summary in items:
        if has_root_manifest_sync_evidence(release_summary):
            candidate_release_tags.add(str(release_summary['releaseTagName']).strip().lower())
    return candidate_release_tags


def normalize_manifest_records(payload, manifest_source):
    # Keep the manifest contract intentionally small so future providers can
    # extend the upstream payload without forcing GithubMirrorLink prop changes.
    payload_dict = payload if isinstance(payload, dict) else {}
    manifest_version = payload_dict.get('version')
    expected_version = manifest_source.get('manifestVersion', manifest_source.get('expectedVersion'))
    if expected_version is not None and manifest_version != expected_version:
        raise ValueError(
            f"Manifest version mismatch for {manifest_source['repositoryKey']}: "
            f"expected {expected_version}, got {manifest_version!r}"
        )

    raw_records = payload_dict.get('records') if isinstance(payload, dict) else payload
    if not isinstance(raw_records, list):
        raise ValueError('Manifest payload must provide a records array')

    normalized_records = []
    for record in raw_records:
        if not isinstance(record, dict):
            continue

        repository_key = str(record.get('repositoryKey') or payload_dict.get('repositoryKey') or '').strip().strip('/')
        provider = record.get('provider')
        provider_key = normalize_provider_key(
            record.get('providerKey')
            or record.get('providerName')
            or (provider.get('key') if isinstance(provider, dict) else provider)
        )
        release_tag_name = str(record.get('releaseTagName') or record.get('release') or '').strip()
        asset_name = str(record.get('assetName') or record.get('asset') or '').strip()
        share_url = str(record.get('shareUrl') or record.get('share_url') or record.get('publicUrl') or '').strip()
        paid_share_url = str(record.get('paidShareUrl') or record.get('paid_share_url') or '').strip() or None
        status = str(record.get('status') or '').strip().lower() or 'unknown'
        synced_at = (
            record.get('syncedAt')
            or record.get('lastSyncedAt')
            or record.get('firstSyncedAt')
            or record.get('updatedAt')
            or payload_dict.get('updatedAt')
        )
        display_name = (
            record.get('displayName')
            or record.get('providerDisplayName')
            or record.get('providerName')
            or provider_key
        )

        if not repository_key or not release_tag_name or not asset_name or not provider_key:
            continue

        normalized_records.append({
            'repositoryKey': repository_key,
            'releaseTagName': release_tag_name,
            'assetName': asset_name,
            'providerKey': provider_key,
            'displayName': display_name,
            'shareUrl': share_url,
            'paidShareUrl': paid_share_url,
            'status': status,
            'syncedAt': synced_at,
            'source': manifest_source.get('source', 'syncer-r2'),
        })

    return [
        record for record in normalized_records
        if record['status'] == 'synced' and record['shareUrl']
    ]


def fetch_manifest_records(manifest_source, release_tag_name=None):
    validated_source = validate_manifest_source(manifest_source)
    if not validated_source:
        return []

    root_index = fetch_root_manifest_index(validated_source)
    repository = root_index.get('repositoriesByKey', {}).get(validated_source['repositoryKey'])
    if not repository:
        logger.info("r2 index has no repository %s", validated_source['repositoryKey'])
        return []
    release_key = str(release_tag_name or '').strip().lower()
    release_summary = next(
        (
            release for release in repository.get('releases', [])
            if str(release.get('releaseTagName') or release.get('release') or '').strip().lower() == release_key
        ),
        None,
    )
    if release_tag_name and not release_summary:
        logger.info("r2 index has no release %s @ %s", validated_source['repositoryKey'], release_tag_name)
        return []
    manifest_path = (release_summary or {}).get('manifestPath') or (release_summary or {}).get('path')
    if not manifest_path:
        logger.warning("r2 index entry has no manifest path for %s @ %s", validated_source['repositoryKey'], release_tag_name)
        return []
    validated_source['_manifestPath'] = str(manifest_path).lstrip('/')
    manifest_url = build_manifest_url(validated_source, release_tag_name)
    cache_key = (
        validated_source['repositoryKey'],
        validated_source.get('manifestVersion'),
        release_key,
    )
    if cache_key in MANIFEST_RECORD_CACHE:
        logger.debug(
            "Manifest cache hit for %s @ %s (%s)",
            validated_source['repositoryKey'],
            release_tag_name,
            manifest_url,
        )
        return MANIFEST_RECORD_CACHE[cache_key]

    logger.debug(
        "Fetching manifest records for %s @ %s from %s",
        validated_source['repositoryKey'],
        release_tag_name,
        manifest_url,
    )

    try:
        payload_response = requests.get(
            manifest_url,
            headers=MANIFEST_REQUEST_HEADERS,
            timeout=validated_source['timeoutSeconds'],
        )
        payload_response.raise_for_status()
        payload = payload_response.json()
        normalized_records = normalize_manifest_records(payload, validated_source)
        if release_tag_name:
            normalized_records = [
                record for record in normalized_records
                if str(record['releaseTagName']).strip().lower() == str(release_tag_name).strip().lower()
            ]
        logger.debug(
            "Manifest records ready for %s @ %s: %s records across providers %s",
            validated_source['repositoryKey'],
            release_tag_name,
            len(normalized_records),
            summarize_provider_counts(normalized_records),
        )
    except requests.Timeout:
        logger.warning(
            "Manifest request timed out for %s @ %s (%s)",
            validated_source['repositoryKey'],
            release_tag_name,
            manifest_url,
        )
        normalized_records = []
    except requests.RequestException as exc:
        logger.warning(
            "Manifest request failed for %s @ %s: %s",
            validated_source['repositoryKey'],
            release_tag_name,
            exc,
        )
        normalized_records = []
    except json.JSONDecodeError as exc:
        logger.warning(
            "Manifest JSON was invalid for %s @ %s: %s",
            validated_source['repositoryKey'],
            release_tag_name,
            exc,
        )
        normalized_records = []
    except ValueError as exc:
        logger.warning(
            "Manifest payload was rejected for %s @ %s: %s",
            validated_source['repositoryKey'],
            release_tag_name,
            exc,
        )
        normalized_records = []

    MANIFEST_RECORD_CACHE[cache_key] = normalized_records
    return normalized_records


def load_github_releases_from_html(owner, repo):
    releases_page_url = f"https://github.com/{owner}/{repo}/releases"
    releases_page_resp = requests.get(
        releases_page_url,
        headers=GITHUB_REQUEST_HEADERS,
        timeout=30,
    )
    releases_page_resp.raise_for_status()

    fragment_pattern = re.compile(
        rf'(?:src|data-deferred-src)="(?P<url>https://github\.com/{re.escape(owner)}/{re.escape(repo)}/releases/expanded_assets/[^"]+)"'
    )
    asset_pattern = re.compile(
        rf'<a href="(?P<href>/{re.escape(owner)}/{re.escape(repo)}/releases/download/[^"]+)"[^>]*class="Truncate">.*?<span[^>]*class="Truncate-text text-bold">(?P<name>.*?)</span>',
        re.S,
    )

    fragment_urls = []
    for match in fragment_pattern.finditer(releases_page_resp.text):
        fragment_url = html.unescape(match.group("url"))
        if fragment_url not in fragment_urls:
            fragment_urls.append(fragment_url)

    releases = []
    for fragment_url in fragment_urls:
        fragment_resp = requests.get(
            fragment_url,
            headers=GITHUB_REQUEST_HEADERS,
            timeout=30,
        )
        fragment_resp.raise_for_status()

        seen_downloads = set()
        assets = []
        for asset_match in asset_pattern.finditer(fragment_resp.text):
            href = html.unescape(asset_match.group("href"))
            download_url = f"https://github.com{href}"
            if download_url in seen_downloads:
                continue
            seen_downloads.add(download_url)
            assets.append({
                "browser_download_url": download_url,
                "name": html.unescape(asset_match.group("name")).strip(),
            })

        releases.append({
            "tag_name": unquote(fragment_url.rsplit("/", 1)[-1]),
            "assets": assets,
        })

    return releases

@task
def create_mirrors(c):
    mirrors_def = load_mirrors_def()
    total = len(mirrors_def['mirrors'])
    logger.info("Starting mirror update run with %s mirror definitions", total)

    # Detect 123pan resource changes from the r2 index/manifest before
    # regenerating content. The resulting doc diff (after generation) is what
    # triggers a publish; this detection makes the 123pan signal explicit and
    # ensures an unavailable 123pan source is diagnosed rather than masked.
    pan123 = detect_123pan_changes(mirrors_def)
    logger.info(
        "123pan change signal: changed=%s status=%s source=%s",
        pan123['changed'],
        pan123['status'],
        pan123['diagnostic'],
    )

    index = 1
    failed_mirrors = []
    for mirror in mirrors_def['mirrors']:
        mirror_type = mirror['type']
        software_name = mirror['softwareName']
        logger.info("[%s/%s] Generating %s mirror for %s", index, total, mirror_type, software_name)
        index += 1
        print(mirror['softwareName'])
        try:
            if mirror_type == 'huawei':
                create_huawei_mirror_v2(mirror)
            elif mirror_type == 'github':
                create_github_mirror(mirror)
            elif mirror_type == 'aliyunpan':
                create_aliyunpan_mirror(mirror)
        except Exception as e:
            logger.error(f"Failed to create mirror for {software_name}: {e}")
            failed_mirrors.append(software_name)
            continue

    logger.info(
        "Mirror update run finished: succeeded=%s failed=%s total=%s",
        total - len(failed_mirrors),
        len(failed_mirrors),
        total,
    )
    if failed_mirrors:
        logger.warning(f"Failed mirrors: {', '.join(failed_mirrors)}")
    else:
        logger.info("All mirrors created successfully!")


def _resolve_repository_key(mirror):
    """Derive the manifest repositoryKey the same way create_github_mirror does.

    This keeps 123pan detection aligned with the manifest actually fetched
    during mirror generation.
    """
    manifest_source = mirror.get('manifestSource')
    if not manifest_source:
        return None
    repository_key = mirror.get('repositoryKey')
    if not repository_key:
        official_site = mirror.get('officialSite', '')
        match = re.search(r'github.com/([^/]+)/([^/]+)', official_site)
        if match:
            repository_key = f'{match.group(1)}/{match.group(2)}'
    return repository_key


def build_123pan_snapshot(mirrors_def):
    """Collect 123pan resource sync state from the r2 index/manifest.

    Walks every configured mirror with a manifest source, reads the r2 root
    index and the per-release manifest the same way ``create_mirrors`` does,
    and collects the 123pan records (keyed by ``repositoryKey:releaseTagName:assetName``)
    with their latest ``syncedAt`` and resolved ``shareUrl``.

    Returns ``(payload, errors)``. A non-empty ``errors`` list means one or more
    manifest sources could not be read, so the 123pan state is only partially
    known and must NOT be silently treated as unchanged by callers.
    """
    snapshot = {}
    errors = []

    for mirror in mirrors_def['mirrors']:
        manifest_source = mirror.get('manifestSource')
        if not manifest_source:
            continue
        try:
            repository_key = _resolve_repository_key(mirror)
            source_with_key = {**manifest_source, 'repositoryKey': repository_key}
            validated_source = validate_manifest_source(source_with_key)
            catalog = get_repository_root_manifest_catalog(validated_source)
            if catalog['state'] != 'guided':
                errors.append(
                    f"{repository_key}: {catalog.get('reason')} "
                    f"({catalog.get('diagnostic')})"
                )
                continue
            release_summaries = catalog.get('releaseSummariesByTag', {})
            for release_tag in release_summaries:
                records = fetch_manifest_records(validated_source, release_tag)
                for record in records:
                    if record.get('providerKey') != '123pan':
                        continue
                    key = ':'.join([
                        record.get('repositoryKey', ''),
                        record.get('releaseTagName', ''),
                        record.get('assetName', ''),
                    ])
                    snapshot[key] = {
                        'syncedAt': record.get('syncedAt'),
                        'shareUrl': record.get('shareUrl'),
                        'status': record.get('status'),
                    }
        except Exception as exc:  # noqa: BLE001 - surface as diagnostic, never mask as synced
            errors.append(f"{_resolve_repository_key(mirror) or 'unknown'}: {exc}")

    payload = {
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'recordCount': len(snapshot),
        'records': dict(sorted(snapshot.items())),
        'errors': errors,
    }
    return payload, errors


def detect_123pan_changes(mirrors_def, baseline_path="tools/123pan-sync-state.json"):
    """Detect whether the 123pan resource state changed since the last run.

    Compares the freshly built 123pan snapshot (from the r2 index/manifest)
    against a previously persisted baseline file. Returns a dict with:

    - ``changed``: ``True`` when the snapshot differs from the baseline, the
      baseline is missing, or a source was unavailable (never silently synced).
    - ``status``: ``available`` or ``unavailable``.
    - ``diagnostic``: human-readable reason.
    - ``record_count``: number of 123pan records observed this run.

    The updated snapshot is written to ``baseline_path`` so the next run can
    compare against it.
    """
    payload, errors = build_123pan_snapshot(mirrors_def)

    if errors:
        diagnostic = (
            "123pan manifest source unavailable; 123pan change detection "
            f"could not complete: {'; '.join(errors)}"
        )
        logger.warning("123pan resource state %s", diagnostic)
        # Persist the partial snapshot so the failure is visible, then report
        # that 123pan state is unavailable (NOT treated as unchanged/synced).
        _write_123pan_snapshot(payload, baseline_path)
        return {
            'changed': True,
            'status': 'unavailable',
            'diagnostic': diagnostic,
            'record_count': payload['recordCount'],
        }

    new_records = payload['records']
    previous = _read_123pan_baseline(baseline_path)
    changed = previous != new_records

    _write_123pan_snapshot(payload, baseline_path)

    if changed:
        if previous is None:
            diagnostic = "123pan baseline missing; treating current state as the first observed snapshot"
        else:
            diagnostic = "123pan resource state differs from previous baseline"
    else:
        diagnostic = "123pan resource state matches previous baseline"

    logger.info("123pan resource state: %s (%s records)", diagnostic, payload['recordCount'])
    return {
        'changed': changed,
        'status': 'available',
        'diagnostic': diagnostic,
        'record_count': payload['recordCount'],
    }


def _read_123pan_baseline(baseline_path):
    try:
        with open(baseline_path, encoding='utf-8') as fh:
            return json.load(fh).get('records', {})
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _write_123pan_snapshot(payload, baseline_path):
    directory = os.path.dirname(baseline_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(baseline_path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write('\n')


def create_huawei_mirror(mirror):
    software_name = mirror['softwareName']
    official_site = mirror['officialSite']
    huawei_mirror_url = mirror['huaweiMirrorUrl']
    version_regex = mirror['versionRegex']
    markdown_filename = mirror['markdownFilename']
    create_date = mirror['createDate']
    desc_section = load_description(software_name)

    post = f"""---
date: {create_date}
title: {software_name}
tags:
  - {software_name}
  - Mirrors
  - 加速下载
  - 镜像加速
  - 国内加速
top: -99
---

{software_name}. 国内直接从官网 {official_site} 下载比较困难，需要一些技术手段。这里提供一个国内的镜像下载地址列表，方便网友下载。

{desc_section}

<!-- more -->

"""
    resp = requests.get(huawei_mirror_url)
    tbody_xml = get_tbody_xml(resp.text)
    all_a = tbody_xml.getElementsByTagName('a')
    section_index = 0
    grouped_a = {}
    for a in all_a:
        match = re.match(version_regex, a.getAttribute('href'))
        v = get_version_name(match.group(0)) if match else "unknown"
        a_list = grouped_a[v] if v in grouped_a else []
        a_list.append(a)
        grouped_a[v] = a_list
    grouped_a.pop('unknown')
    version_count = len(grouped_a)
    groups = []
    for g in grouped_a:
        links = sorted(grouped_a[g], key=lambda a_element: get_version_order(
            a_element.getAttribute('href')))
        groups.append((g, links))

    groups.sort(key=lambda item: get_version_order(item[0]))
    offset = 10 if version_count > 10 else 0
    for g in groups:
        post += get_huawei_version_section(huawei_mirror_url, g[1], g[0])
        if section_index == version_count - offset:
            post += f"""

<img src='/images/weixin_public.png' alt='微信' />

"""
        section_index += 1
    post += f"""

找不到想要的版本？您可以访问 [索引页]({huawei_mirror_url}) 以下载更多版本。

<!-- md Mirrors.md -->


"""
    with open(f'../docs/Mirrors/{markdown_filename}', 'w', encoding='utf8') as f:
        f.write(post)


def create_huawei_mirror_v2(mirror):
    software_name = mirror['softwareName']
    official_site = mirror['officialSite']
    huawei_mirror_url = mirror['huaweiMirrorUrl']
    version_regex = mirror['versionRegex']
    markdown_filename = mirror['markdownFilename']
    create_date = mirror['createDate']
    desc_section = load_description(software_name)

    post = f"""---
date: {create_date}
title: {software_name}
tags:
  - {software_name}
  - Mirrors
  - 加速下载
  - 镜像加速
  - 国内加速
top: -99
---

{software_name}. 国内直接从官网 {official_site} 下载比较困难，需要一些技术手段。这里提供一个国内的镜像下载地址列表，方便网友下载。

{desc_section}

<img src='/images/weixin_public.png' alt='微信' />

<!-- more -->

"""
    resp = requests.get(huawei_mirror_url)
    tbody_xml = get_html_xml(resp.text)
    all_a = tbody_xml.getElementsByTagName('a')
    section_index = 0
    grouped_a = {}
    for a in all_a:
        match = re.match(version_regex, a.getAttribute('href'))
        v = get_version_name(match.group(0)) if match else "unknown"
        a_list = grouped_a[v] if v in grouped_a else []
        a_list.append(a)
        grouped_a[v] = a_list
    if 'unknown' in grouped_a.keys():
        grouped_a.pop('unknown')
    version_count = len(grouped_a)
    groups = []
    for g in grouped_a:
        links = sorted(grouped_a[g], key=lambda a_element: get_version_order(
            a_element.getAttribute('href')))
        groups.append((g, links))

    groups.sort(key=lambda item: get_version_order(item[0]))
    offset = 10 if version_count > 10 else 0
    for g in groups:
        post += get_huawei_version_section_v2(huawei_mirror_url, g[1], g[0])
        if section_index == version_count - offset:
            post += f"""



"""
        section_index += 1
    post += f"""

找不到想要的版本？您可以访问 [索引页]({huawei_mirror_url}) 以下载更多版本。


<!-- md Mirrors.md -->


"""
    with open(f'../docs/Mirrors/{markdown_filename}', 'w', encoding='utf8') as f:
        f.write(post)


# def create_github_mirror(mirror):
#     software_name = mirror['softwareName']
#     official_site = mirror['officialSite']
#     owner = mirror['owner']
#     repo = mirror['repo']
#     mirror_prefix = mirror['mirrorPrefix']
#     markdown_filename = mirror['markdownFilename']
#     create_date = mirror['createDate']

#     desc_section = load_description(software_name)

#     post = f"""---
# date: {create_date}
# title: {software_name}
# tags:
#   - {software_name}
#   - Mirrors
#   - 加速下载
#   - 镜像加速
#   - 国内加速
# top: -99
# ---

# {software_name}. 目前加速功能已经失效，请前往 <{official_site}> 下载。

# {desc_section}

# <!-- more -->

# """

#     post += f"""


# <!-- md Mirrors.md -->


# """
#     with open(f'../docs/Mirrors/{markdown_filename}', 'w', encoding='utf8') as f:
#         f.write(post)

def create_github_mirror(mirror):
    software_name = mirror['softwareName']
    # https://github.com/{owner}/{repo}/
    official_site = mirror['officialSite']
    # exact owner and repo from official_site
    owner = re.search(r'github.com/([^/]+)/([^/]+)', official_site).group(1)
    repo = re.search(r'github.com/([^/]+)/([^/]+)', official_site).group(2)
    markdown_filename = mirror['markdownFilename']
    create_date = mirror['createDate']
    repository_key = mirror.get('repositoryKey', f'{owner}/{repo}')
    preferred_providers = [
        normalize_provider_key(provider)
        for provider in mirror.get('preferredProviders', [])
        if str(provider).strip()
    ]
    manifest_source = {
        **mirror.get('manifestSource', {}),
        'repositoryKey': repository_key,
    } if mirror.get('manifestSource') else None
    manifest_catalog = (
        get_repository_root_manifest_catalog(manifest_source)
        if manifest_source
        else None
    )
    desc_section = load_description(software_name)
    logger.debug(
        "Starting GitHub mirror generation for %s (%s)",
        software_name,
        repository_key,
    )

    post = f"""---
date: {create_date}
title: {software_name}
tags:
  - {software_name}
  - Mirrors
  - 加速下载
  - 镜像加速
  - 国内加速
top: -99
---

{software_name}. 国内直接从官网 {official_site} 下载比较困难，需要一些技术手段。这里提供一个国内的镜像下载地址列表，方便网友下载。

{desc_section}

import GithubMirrorLink from '../../src/components/GithubMirrorLink';

"""
    github_api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    resp = requests.get(
        github_api_url,
        headers=github_api_headers(),
        timeout=30,
    )
    releases = resp.json()
    markdown_path = f'../docs/Mirrors/{markdown_filename}'
    if not isinstance(releases, list):
        logger.warning(
            "GitHub API returned %s for %s/%s, trying HTML fallback before existing markdown",
            type(releases).__name__,
            owner,
            repo,
        )
        # The GitHub API call failed (e.g. rate limit / auth error). The HTML
        # scrape is a degraded fallback: it only sees the first releases page and
        # frequently extracts zero assets, so it must never overwrite a doc that
        # already has good content. Keep the previous version instead of
        # blanking or truncating it.
        if os.path.exists(markdown_path):
            logger.warning(
                "GitHub API unavailable for %s/%s; preserving existing %s instead of overwriting with degraded HTML scrape",
                owner,
                repo,
                markdown_path,
            )
            remove_hagicode_promo_from_existing_doc(markdown_path)
            return
        releases = load_github_releases_from_html(owner, repo)
        if not releases:
            raise RuntimeError(f"Unable to fetch releases for {owner}/{repo} from API or HTML fallback")
    elif not releases:
        # GitHub API returned an empty list; never blank an existing doc.
        if os.path.exists(markdown_path):
            logger.warning(
                "GitHub API returned an empty release list for %s/%s; preserving existing %s",
                owner,
                repo,
                markdown_path,
            )
            remove_hagicode_promo_from_existing_doc(markdown_path)
            return
        raise RuntimeError(f"GitHub API returned no releases for {owner}/{repo}")
    if releases:
        releases = sorted(releases, key=lambda item: item.get('published_at') or '', reverse=True)

    version_count = len(releases)
    section_index = 0
    offset = 10 if version_count > 10 else 0
    total_assets = 0
    for section_index, release in enumerate(releases, start=1):
        release_tag_name = str(release.get('tag_name') or '').strip()
        release_assets = release.get('assets', [])
        total_assets += len(release_assets)
        should_fetch_manifest = (
            manifest_source
            and (
                manifest_catalog['state'] != 'guided'
                or release_tag_name.lower() in manifest_catalog['candidateReleaseTags']
            )
        )
        resolved_records = (
            fetch_manifest_records(manifest_source, release_tag_name)
            if should_fetch_manifest
            else []
        )
        matching_records = [
            record for record in resolved_records
            if record.get('repositoryKey') == repository_key
            and str(record.get('releaseTagName', '')).strip().lower() == release_tag_name.lower()
        ]
        records_by_asset = {}
        for record in matching_records:
            if (
                record.get('status') == 'synced'
                and record.get('shareUrl')
            ):
                records_by_asset.setdefault(record['assetName'], []).append(record)
        used_count = sum(len(records) for records in records_by_asset.values())
        logger.info(
            "syncer r2 manifest summary for %s @ %s: discovered=%s used=%s skipped=%s",
            repository_key,
            release_tag_name,
            len(matching_records),
            used_count,
            len(matching_records) - used_count,
        )
        post += get_github_version_section(
            release,
            repository_key=repository_key,
            preferred_providers=preferred_providers,
            resolved_mirrors_by_asset=records_by_asset,
            is_latest=section_index == 1,
        )
        if section_index == version_count - offset:
            post += f"""

"""

    post += f"""

找不到想要的版本？您可以访问 [官方网站]({official_site}) 以下载更多版本。

<!-- md Mirrors.md -->


"""
    with open(markdown_path, 'w', encoding='utf8') as f:
        f.write(post)
    logger.info(
        "Finished GitHub mirror generation for %s (%s): releases=%s, assets=%s, output=%s",
        software_name,
        repository_key,
        version_count,
        total_assets,
        markdown_path,
    )

def create_aliyunpan_mirror(mirror):
    software_name = mirror['softwareName']
    official_site = mirror['officialSite']
    owner = mirror['owner']
    repo = mirror['repo']
    mirror_prefix = mirror['mirrorPrefix']
    markdown_filename = mirror['markdownFilename']
    create_date = mirror['createDate']

    desc_section = load_description(software_name)

    post = f"""---
date: {create_date}
title: {software_name}
tags:
  - {software_name}
  - Mirrors
  - 加速下载
  - 镜像加速
  - 国内加速
top: -99
---

{software_name}. 国内直接从官网 {official_site} 下载比较困难，需要一些技术手段。这里提供一个国内的镜像下载地址列表，方便网友下载。

{desc_section}

<!-- more -->

"""
    github_api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    resp = requests.get(github_api_url)
    releases = resp.json()
    releases = sorted(releases, key=lambda item: item['published_at'])
    version_count = len(releases)
    section_index = 0
    offset = 10 if version_count > 10 else 0
    for release in releases:
        section_index += 1
        post += get_github_version_section(release)
        if section_index >= version_count - offset:
            break

    post += f"""

若要查看完整列表，可以通过阿里云盘「release mirror」，你可以不限速下载🚀
复制这段内容打开「阿里云盘」App 即可获取
链接：https://www.aliyundrive.com/s/QN9uNcaeZDS


<!-- md Mirrors.md -->


"""
    with open(f'../docs/Mirrors/{markdown_filename}', 'w', encoding='utf8') as f:
        f.write(post)