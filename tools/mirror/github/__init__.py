import json


def get_github_version_section(
    release,
    repository_key=None,
    preferred_providers=None,
    resolved_mirrors_by_asset=None,
):
    content = ""
    preferred_providers = preferred_providers or []
    resolved_mirrors_by_asset = resolved_mirrors_by_asset or {}

    for asset in release['assets']:
        props = [
            f'link={json.dumps(asset["browser_download_url"], ensure_ascii=False)}',
            f'text={json.dumps(asset["name"], ensure_ascii=False)}',
        ]

        if repository_key:
            props.append(f'repositoryKey={json.dumps(repository_key, ensure_ascii=False)}')
        resolved_mirrors = resolved_mirrors_by_asset.get(asset["name"], [])
        if resolved_mirrors:
            resolved_payload = [
                {
                    "providerKey": record["providerKey"],
                    "fullUrl": record["shareUrl"],
                    "displayName": record["displayName"],
                    "source": record["source"],
                    "status": record["status"],
                    "syncedAt": record["syncedAt"],
                }
                for record in resolved_mirrors
            ]
            if preferred_providers:
                props.append(f'preferredProviders={{{json.dumps(preferred_providers, ensure_ascii=False)}}}')
            props.append(f'resolvedMirrors={{{json.dumps(resolved_payload, ensure_ascii=False)}}}')

        content += f"- <GithubMirrorLink {' '.join(props)} />\n"

    result = f"""
## {release['tag_name']}

{content}

"""
    return result
