# -*- coding: UTF-8 -*-

import json
import logging
import re

import requests
from invoke import task

from mirror.github import get_github_version_section
from mirror.huawei import get_version_name, get_tbody_xml, get_version_order, get_huawei_version_section, get_html_xml, get_huawei_version_section_v2
from mirror import load_description

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

logger = logging.getLogger()
MIRROR_DEF_JSON_PATH = "mirrorsDef.json"

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
        insert_markers = ["<OneDrive />", "## "]
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
    elif "<OneDrive />" in post:
        promo_index = post.find(HAGICODE_PROMO_BLOCK)
        onedrive_index = post.find("<OneDrive />")
        if promo_index > onedrive_index:
            post = post.replace(f"\n{HAGICODE_PROMO_BLOCK}\n", "\n", 1)
            post = post[:onedrive_index] + f"{HAGICODE_PROMO_BLOCK}\n\n" + post[onedrive_index:]

    with open(markdown_path, 'w', encoding='utf8') as f:
        f.write(post)

def load_mirrors_def():
    mirrors_def = json.load(open(MIRROR_DEF_JSON_PATH))
    logger.debug(f'mirrors def load: {mirrors_def}')
    # sort by software name
    mirrors_def['mirrors'].sort(key=lambda item: item['softwareName'])
    return mirrors_def

@task
def create_mirrors(c):
    mirrors_def = load_mirrors_def()
    total = len(mirrors_def['mirrors'])
    index = 1
    failed_mirrors = []
    for mirror in mirrors_def['mirrors']:
        logger.info(f"{index} / {total}")
        index += 1
        mirror_type = mirror['type']
        software_name = mirror['softwareName']
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
    # get oneDriveSupport else False
    one_drive_support = mirror.get('oneDriveSupport', False)
    # exact owner and repo from official_site
    owner = re.search(r'github.com/([^/]+)/([^/]+)', official_site).group(1)
    repo = re.search(r'github.com/([^/]+)/([^/]+)', official_site).group(2)
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
import GithubMirrorLink from '../../src/components/GithubMirrorLink';
import OneDrive from './_onedrive.md';

"""
    post += f"""
{get_hagicode_promo_block()}
"""
    if one_drive_support:
        post += f"""
        <OneDrive />
        """
    github_api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    resp = requests.get(github_api_url)
    releases = resp.json()
    markdown_path = f'../docs/Mirrors/{markdown_filename}'
    if not isinstance(releases, list):
        logger.warning(
            "GitHub API returned %s for %s/%s, falling back to existing markdown",
            type(releases).__name__,
            owner,
            repo,
        )
        ensure_hagicode_promo_in_existing_doc(markdown_path)
        return
    # sort desc
    releases = sorted(releases, key=lambda item: item['published_at'], reverse=True)
    version_count = len(releases)
    section_index = 0
    offset = 10 if version_count > 10 else 0
    for release in releases:
        section_index += 1
        post += get_github_version_section(release, mirror_prefix, one_drive_support)
        if section_index == version_count - offset:
            post += f"""

"""

    post += f"""

找不到想要的版本？您可以访问 [官方网站]({official_site}) 以下载更多版本。

<!-- md Mirrors.md -->


"""
    with open(markdown_path, 'w', encoding='utf8') as f:
        f.write(post)

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
        post += get_github_version_section(release, mirror_prefix)
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
