def get_github_version_section(release, mirror_prefix, one_drive_support):
    content = ""
    template = """- <GithubMirrorLink link={"#link#"} text="#text#" oneDriveSupport={#one_drive_support#} />
"""
    for asset in release['assets']:
        content += template.replace("#link#", asset['browser_download_url']).replace("#text#", asset['name']).replace("#one_drive_support#", str(one_drive_support).lower())
    result = f"""
## {release['tag_name']}

{content}

"""
    return result
