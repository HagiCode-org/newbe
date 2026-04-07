import os


def load_description(software_name, description=None):
    path = f"MirrorDescription/{software_name}.md"
    content = None
    if os.path.exists(path):
        with open(path, encoding="utf8") as f:
            content = f.read()
    else:
        with open(path, "w", encoding="utf8") as ff:
            pass
    content = content if content else " "
    re = content if content else description
    return re
