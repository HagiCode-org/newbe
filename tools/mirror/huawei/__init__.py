import xml.dom.minidom
import re
from xml.dom.minidom import parse


def get_huawei_version_section(base_url, group_info, version):
    content = ""
    for info in group_info:
        content += f"""- [{info.getAttribute('title')}]({base_url + info.getAttribute('href')})
"""
    result = f"""
## {version}

{content}

"""
    return result


def get_huawei_version_section_v2(base_url, group_info, version):
    content = ""
    for info in group_info:
        content += f"""- [{info.getAttribute('href').strip('/')}]({base_url + info.getAttribute('href')})
"""
    result = f"""
## {version}

{content}

"""
    return result


def get_tbody_xml(content: str) -> object:
    start_index = content.index('<tbody>')
    tbody = content[start_index:]
    end_index = tbody.index('</tbody>')
    tbody = tbody[:end_index]
    tbody += '</tbody>'
    return xml.dom.minidom.parseString(tbody)


def get_html_xml(content: str) -> object:
    try:
        start_index = content.index('<pre>')
        tbody = content[start_index+len('<pre>'):]
        # 2nd pre
        start_index = tbody.index('<pre>')
        tbody = tbody[start_index:]
        end_index = tbody.index('</pre>')
        tbody = tbody[:end_index]
        tbody += '</pre>'
        return xml.dom.minidom.parseString(tbody)
    except (ValueError, Exception) as e:
        # Fallback: try to parse with tbody if pre tags are not found
        try:
            start_index = content.index('<tbody>')
            tbody = content[start_index:]
            end_index = tbody.index('</tbody>')
            tbody = tbody[:end_index]
            tbody += '</tbody>'
            return xml.dom.minidom.parseString(tbody)
        except (ValueError, Exception):
            # Last resort: return empty parsed XML
            return xml.dom.minidom.parseString('<tbody></tbody>')


def get_version_name(source_version: str) -> str:
    name = source_version
    v = name
    match1 = re.search(r"(\d+)\.(\d+)\.(\d+)\.?", name)
    match2 = re.search(r"(\d+)\.(\d+)\.?", name)
    # three
    if match1:
        v = f"{match1.group(1)}.{match1.group(2)}.{match1.group(2)}"
    elif match2:
        v = f"{match2.group(1)}.{match2.group(2)}"
    return v


def get_version_order(source_version: str) -> str:
    name = source_version
    v = name
    match1 = re.search(r"(\d+)\.(\d+)\.(\d+)\.?", name)
    match2 = re.search(r"(\d+)\.(\d+)\.?", name)
    # three
    if match1:
        v = f"{int(match1.group(1)):04,d}.{int(match1.group(2)):04,d}.{int(match1.group(3)):04,d}"
    elif match2:
        v = f"{int(match2.group(1)):04,d}.{int(match2.group(2)):04,d}"
    return v
