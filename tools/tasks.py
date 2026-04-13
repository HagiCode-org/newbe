# -*- coding: UTF-8 -*-

import html
import json
import logging
import os
import re
from urllib.parse import quote, unquote, urlsplit, urlunsplit

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
MANIFEST_REQUEST_HEADERS = {
    "User-Agent": "HagiCode-Mirror-Manifest/1.0",
    "Accept": "application/json",
}
MANIFEST_RECORD_CACHE = {}
ROOT_MANIFEST_INDEX_CACHE = {}
DEFAULT_MANIFEST_BLOB_PREFIX = 'release-sync'

HAGICODE_PROMO_IMPORT = "import HagicodeRecommendation from '../../src/components/HagicodeRecommendation';"
HAGICODE_PROMO_BLOCK = "<HagicodeRecommendation layout=\"page\" />"


def get_hagicode_promo_mdx():
    return f"""
{HAGICODE_PROMO_IMPORT}
"""


def get_hagicode_promo_block():
    return f"""
{HAGICODE_PROMO_BLOCK}

"""


def ensure_hagicode_promo_in_existing_doc(markdown_path):
    with open(markdown_path, 'r', encoding='utf8') as f:
        post = f.read()

    if HAGICODE_PROMO_IMPORT not in post:
        if "import GithubMirrorLink" in post:
            post = post.replace(
                "import GithubMirrorLink",
                f"{HAGICODE_PROMO_IMPORT}\nimport GithubMirrorLink",
                1,
            )
        else:
            frontmatter_end = post.find('\n---\n', 4)
            if frontmatter_end != -1:
                post = f"{post[:frontmatter_end + 5]}\n{HAGICODE_PROMO_IMPORT}\n{post[frontmatter_end + 5:]}"

    if HAGICODE_PROMO_BLOCK not in post:
        insert_markers = ["## "]
        insert_index = -1
        for marker in insert_markers:
            marker_index = post.find(marker)
            if marker_index != -1:
                insert_index = marker_index
                break

        if insert_index == -1:
            post = f"{post.rstrip()}\n\n{HAGICODE_PROMO_BLOCK}\n"
        else:
            post = f"{post[:insert_index]}{HAGICODE_PROMO_BLOCK}\n\n{post[insert_index:]}"

    with open(markdown_path, 'w', encoding='utf8') as f:
        f.write(post)

def load_mirrors_def():
    mirrors_def = json.load(open(MIRROR_DEF_JSON_PATH))
    logger.debug(f'mirrors def load: {mirrors_def}')
    # sort by software name
    mirrors_def['mirrors'].sort(key=lambda item: item['softwareName'])
    return mirrors_def


def normalize_provider_key(provider_name):
    if not provider_name:
        return None
    normalized = str(provider_name).strip().lower()
    if normalized in {'pan123', '123 pan', '123-pan', '123_pan'}:
        return '123pan'
    return normalized


def summarize_provider_counts(records):
    provider_counts = {}
    for record in records or []:
        provider_key = record.get('providerKey') or 'unknown'
        provider_counts[provider_key] = provider_counts.get(provider_key, 0) + 1
    return provider_counts


def summarize_matched_provider_counts(provider_links_by_asset):
    provider_counts = {}
    for matched_links in (provider_links_by_asset or {}).values():
        for link in matched_links:
            provider_key = link.get('providerKey') or 'unknown'
            provider_counts[provider_key] = provider_counts.get(provider_key, 0) + 1
    return provider_counts


def split_repository_key(repository_key):
    normalized_repository_key = str(repository_key or '').strip().strip('/')
    owner_repo = [segment for segment in normalized_repository_key.split('/') if segment]
    if len(owner_repo) != 2:
        raise ValueError('manifestSource.repositoryKey must use the "<owner>/<repo>" format')
    return owner_repo[0], owner_repo[1]


def normalize_manifest_blob_prefix(prefix):
    normalized_prefix = str(prefix or DEFAULT_MANIFEST_BLOB_PREFIX).strip().strip('/')
    return normalized_prefix or DEFAULT_MANIFEST_BLOB_PREFIX


def resolve_manifest_container_sas_url(manifest_source):
    if not manifest_source:
        return None
    direct_url = manifest_source.get('containerSasUrl')
    if direct_url:
        return str(direct_url).strip()
    url_env = manifest_source.get('containerSasUrlEnv')
    if not url_env:
        return None
    resolved_url = os.getenv(url_env)
    return resolved_url.strip() if resolved_url else None


def build_release_sync_manifest_blob_name(repository_key, release_tag_name, prefix=DEFAULT_MANIFEST_BLOB_PREFIX):
    if not release_tag_name or not str(release_tag_name).strip():
        return None

    owner, repo = split_repository_key(repository_key)
    segments = [
        *normalize_manifest_blob_prefix(prefix).split('/'),
        owner,
        repo,
        str(release_tag_name).strip(),
        'manifest.json',
    ]
    return '/'.join(segments)


def build_root_manifest_index_blob_name(prefix=DEFAULT_MANIFEST_BLOB_PREFIX):
    segments = [
        *normalize_manifest_blob_prefix(prefix).split('/'),
        'index.json',
    ]
    return '/'.join(segments)


def build_blob_url(container_sas_url, blob_name):
    parsed_url = urlsplit(container_sas_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError('manifestSource.containerSasUrl must be an absolute URL')

    encoded_blob_name = '/'.join(quote(segment, safe='') for segment in blob_name.split('/'))
    blob_path = f"{parsed_url.path.rstrip('/')}/{encoded_blob_name}"

    return urlunsplit((
        parsed_url.scheme,
        parsed_url.netloc,
        blob_path,
        parsed_url.query,
        parsed_url.fragment,
    ))


def build_manifest_url(manifest_source, release_tag_name):
    container_sas_url = manifest_source.get('containerSasUrl')
    if not container_sas_url:
        return None

    blob_name = build_release_sync_manifest_blob_name(
        manifest_source['repositoryKey'],
        release_tag_name,
        manifest_source.get('blobPrefix', DEFAULT_MANIFEST_BLOB_PREFIX),
    )
    if not blob_name:
        return None

    return build_blob_url(container_sas_url, blob_name)


def build_root_manifest_index_url(manifest_source):
    container_sas_url = manifest_source.get('containerSasUrl')
    if not container_sas_url:
        return None
    return build_blob_url(
        container_sas_url,
        build_root_manifest_index_blob_name(
            manifest_source.get('blobPrefix', DEFAULT_MANIFEST_BLOB_PREFIX),
        ),
    )


def validate_manifest_source(manifest_source):
    if not manifest_source:
        return None

    repository_key = manifest_source.get('repositoryKey')
    if not repository_key:
        raise ValueError('manifestSource.repositoryKey is required when manifestSource is configured')
    split_repository_key(repository_key)

    expected_version = manifest_source.get('expectedVersion')
    if expected_version is not None and not isinstance(expected_version, int):
        raise ValueError('manifestSource.expectedVersion must be an integer when provided')

    timeout_seconds = manifest_source.get('timeoutSeconds', 15)
    if not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
        raise ValueError('manifestSource.timeoutSeconds must be a positive integer when provided')

    container_sas_url = resolve_manifest_container_sas_url(manifest_source)
    if not container_sas_url and not (
        manifest_source.get('containerSasUrl') or manifest_source.get('containerSasUrlEnv')
    ):
        raise ValueError('manifestSource must define containerSasUrl or containerSasUrlEnv')

    return {
        'repositoryKey': repository_key,
        'expectedVersion': expected_version,
        'timeoutSeconds': timeout_seconds,
        'source': manifest_source.get('source', 'azure'),
        'blobPrefix': normalize_manifest_blob_prefix(manifest_source.get('blobPrefix')),
        'containerSasUrl': container_sas_url,
        'containerSasUrlEnv': manifest_source.get('containerSasUrlEnv'),
    }


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
            f"Set {validated_source.get('containerSasUrlEnv') or 'manifestSource.containerSasUrl'} to enable root index discovery."
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
        response = requests.get(
            root_index_url,
            headers=MANIFEST_REQUEST_HEADERS,
            timeout=validated_source['timeoutSeconds'],
        )
        response.raise_for_status()
        payload = response.json()
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
            'state': 'legacy',
            'reason': 'manifest_source_missing',
            'diagnostic': 'manifestSource is not configured',
            'releaseSummariesByTag': {},
            'candidateReleaseTags': set(),
        }

    root_manifest_index = fetch_root_manifest_index(validated_source)
    if root_manifest_index.get('state') != 'ready':
        logger.info(
            "Manifest root index unavailable for %s, falling back to legacy probing: %s (%s)",
            validated_source['repositoryKey'],
            root_manifest_index.get('reason', 'root_index_unavailable'),
            root_manifest_index.get('diagnostic'),
        )
        return {
            'state': 'legacy',
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
            "Manifest root index does not include %s, falling back to legacy probing",
            repository_key,
        )
        return {
            'state': 'legacy',
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
    expected_version = manifest_source.get('expectedVersion')
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

        repository_key = record.get('repositoryKey') or payload_dict.get('repositoryKey') or manifest_source['repositoryKey']
        provider_key = normalize_provider_key(record.get('providerName') or record.get('providerKey'))
        release_tag_name = record.get('releaseTagName')
        asset_name = record.get('assetName')
        share_url = (record.get('shareUrl') or '').strip()
        status = str(record.get('status') or '').strip().lower() or 'unknown'
        synced_at = (
            record.get('lastSyncedAt')
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
            'status': status,
            'syncedAt': synced_at,
            'source': manifest_source.get('source', 'azure'),
        })

    return normalized_records


def fetch_manifest_records(manifest_source, release_tag_name=None):
    validated_source = validate_manifest_source(manifest_source)
    if not validated_source:
        return []

    container_sas_url = validated_source.get('containerSasUrl')
    if not container_sas_url:
        logger.warning(
            "Manifest container SAS URL is not configured for %s. Set %s to enable provider links.",
            validated_source['repositoryKey'],
            validated_source.get('containerSasUrlEnv') or 'manifestSource.containerSasUrl',
        )
        return []

    manifest_url = build_manifest_url(validated_source, release_tag_name)
    if not manifest_url:
        logger.warning(
            "Manifest URL could not be derived for %s because release tag is missing.",
            validated_source['repositoryKey'],
        )
        return []

    cache_key = (
        manifest_url,
        validated_source['repositoryKey'],
        validated_source.get('expectedVersion'),
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
        response = requests.get(
            manifest_url,
            headers=MANIFEST_REQUEST_HEADERS,
            timeout=validated_source['timeoutSeconds'],
        )
        response.raise_for_status()
        payload = response.json()
        normalized_records = normalize_manifest_records(payload, validated_source)
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


def build_provider_links_by_asset(release, mirror, manifest_records):
    # Provider links must match the exact repository + release tag + asset name.
    # This prevents stale or cross-product share links from leaking into Ollama.
    manifest_source = mirror.get('manifestSource') or {}
    repository_key = (
        mirror.get('repositoryKey')
        or manifest_source.get('repositoryKey')
        or re.search(r'github.com/([^/]+)/([^/]+)', mirror['officialSite']).group(1) + '/' +
        re.search(r'github.com/([^/]+)/([^/]+)', mirror['officialSite']).group(2)
    )
    normalized_repository_key = repository_key.strip().strip('/')
    normalized_release_tag = str(release.get('tag_name') or '').strip().lower()

    if not normalized_release_tag:
        return {}

    provider_links_by_asset = {}
    for asset in release.get('assets', []):
        asset_name = str(asset.get('name') or '').strip()
        if not asset_name:
            continue

        matched_links = []
        for record in manifest_records:
            if record['repositoryKey'].strip().strip('/') != normalized_repository_key:
                continue
            if str(record['releaseTagName']).strip().lower() != normalized_release_tag:
                continue
            if str(record['assetName']).strip() != asset_name:
                continue
            if record.get('status') != 'synced':
                continue
            share_url = (record.get('shareUrl') or '').strip()
            if not share_url:
                continue
            matched_links.append({
                'providerKey': record['providerKey'],
                'displayName': record['displayName'],
                'fullUrl': share_url,
                'status': record.get('status'),
                'syncedAt': record.get('syncedAt'),
                'source': record.get('source', 'azure'),
            })

        if matched_links:
            provider_links_by_asset[asset_name] = matched_links

    return provider_links_by_asset


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

{get_hagicode_promo_mdx()}
{get_hagicode_promo_block()}

### [点击此处，您也可以部署自己专属的免费 Github 资源加速站点](https://rg.newbe.pro/docs/turbohub/quick-start)

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

### [点击此处，您也可以部署自己专属的免费 Github 资源加速站点](https://rg.newbe.pro/docs/turbohub/quick-start)

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

{get_hagicode_promo_mdx()}
{get_hagicode_promo_block()}

### [点击此处，您也可以部署自己专属的免费 Github 资源加速站点](https://rg.newbe.pro/docs/turbohub/quick-start)

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
    preferred_providers = mirror.get('preferredProviders', [])
    desc_section = load_description(software_name)
    logger.debug(
        "Starting GitHub mirror generation for %s (%s); preferred providers=%s; manifest enabled=%s",
        software_name,
        repository_key,
        preferred_providers,
        bool(mirror.get('manifestSource')),
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

{get_hagicode_promo_mdx()}
import GithubMirrorLink from '../../src/components/GithubMirrorLink';

"""
    post += f"""
{get_hagicode_promo_block()}
"""
    github_api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    resp = requests.get(
        github_api_url,
        headers=GITHUB_REQUEST_HEADERS,
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
        releases = load_github_releases_from_html(owner, repo)
        if not releases:
            if os.path.exists(markdown_path):
                ensure_hagicode_promo_in_existing_doc(markdown_path)
                return
            raise RuntimeError(f"Unable to fetch releases for {owner}/{repo} from API or HTML fallback")
    elif releases and 'published_at' in releases[0]:
        # sort desc
        releases = sorted(releases, key=lambda item: item['published_at'], reverse=True)

    manifest_source = mirror.get('manifestSource')
    manifest_catalog = get_repository_root_manifest_catalog(manifest_source) if manifest_source else {
        'state': 'legacy',
        'reason': 'manifest_source_missing',
        'diagnostic': 'manifestSource is not configured',
        'releaseSummariesByTag': {},
        'candidateReleaseTags': set(),
    }
    if manifest_source and manifest_catalog['state'] == 'legacy':
        logger.info(
            "Root manifest index fallback for %s: %s (%s)",
            repository_key,
            manifest_catalog.get('reason'),
            manifest_catalog.get('diagnostic'),
        )

    version_count = len(releases)
    section_index = 0
    offset = 10 if version_count > 10 else 0
    total_assets = 0
    total_manifest_records = 0
    total_matched_assets = 0
    total_matched_links = 0
    aggregate_provider_counts = {}
    for release in releases:
        section_index += 1
        release_tag_name = str(release.get('tag_name') or '').strip()
        normalized_release_tag = release_tag_name.lower()
        manifest_records = []
        release_assets = release.get('assets', [])
        total_assets += len(release_assets)
        if manifest_source:
            if manifest_catalog['state'] == 'guided':
                if normalized_release_tag in manifest_catalog['candidateReleaseTags']:
                    manifest_records = fetch_manifest_records(manifest_source, release_tag_name)
                else:
                    logger.debug(
                        "Skipping manifest fetch for %s @ %s because the root manifest index has no sync evidence.",
                        repository_key,
                        release_tag_name,
                    )
            else:
                manifest_records = fetch_manifest_records(manifest_source, release_tag_name)
        provider_links_by_asset = build_provider_links_by_asset(release, mirror, manifest_records)
        matched_links_count = sum(len(matched_links) for matched_links in provider_links_by_asset.values())
        matched_provider_counts = summarize_matched_provider_counts(provider_links_by_asset)
        total_manifest_records += len(manifest_records)
        total_matched_assets += len(provider_links_by_asset)
        total_matched_links += matched_links_count
        for provider_key, count in matched_provider_counts.items():
            aggregate_provider_counts[provider_key] = aggregate_provider_counts.get(provider_key, 0) + count
        logger.debug(
            "Release %s for %s: assets=%s, manifest_records=%s, matched_assets=%s, matched_links=%s, matched_providers=%s",
            release_tag_name or '<missing-tag>',
            repository_key,
            len(release_assets),
            len(manifest_records),
            len(provider_links_by_asset),
            matched_links_count,
            matched_provider_counts,
        )
        post += get_github_version_section(
            release,
            repository_key=repository_key,
            preferred_providers=preferred_providers,
            provider_links_by_asset=provider_links_by_asset,
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
        "Finished GitHub mirror generation for %s (%s): releases=%s, assets=%s, manifest_records=%s, matched_assets=%s, matched_links=%s, provider_totals=%s, output=%s",
        software_name,
        repository_key,
        version_count,
        total_assets,
        total_manifest_records,
        total_matched_assets,
        total_matched_links,
        aggregate_provider_counts,
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

{get_hagicode_promo_mdx()}
{get_hagicode_promo_block()}

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
