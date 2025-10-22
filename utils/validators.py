import re
_ABN_RE = re.compile(r"^\s*\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\s*$")
def is_valid_abn(text: str) -> bool:
    return bool(_ABN_RE.match(text or ""))
