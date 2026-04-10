import json


def get_github_version_section(
    release,
    one_drive_support,
    repository_key=None,
    preferred_providers=None,
    provider_links_by_asset=None,
):
    content = ""
    preferred_providers = preferred_providers or []
    provider_links_by_asset = provider_links_by_asset or {}

    for asset in release['assets']:
        props = [
            f'link={json.dumps(asset["browser_download_url"], ensure_ascii=False)}',
            f'text={json.dumps(asset["name"], ensure_ascii=False)}',
            f'oneDriveSupport={str(one_drive_support).lower()}',
        ]

        if repository_key:
            props.append(f'repositoryKey={json.dumps(repository_key, ensure_ascii=False)}')
        if preferred_providers:
            props.append(f'preferredProviders={{{json.dumps(preferred_providers, ensure_ascii=False)}}}')

        matched_provider_links = provider_links_by_asset.get(asset['name']) or []
        if matched_provider_links:
            props.append(f'resolvedMirrors={{{json.dumps(matched_provider_links, ensure_ascii=False)}}}')

        content += f"- <GithubMirrorLink {' '.join(props)} />\n"

    result = f"""
## {release['tag_name']}

{content}

"""
    return result
