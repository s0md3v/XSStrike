import base64 as b64
import re
from typing import Union

def base64_encode(data: Union[str, bytes]) -> str:
    """Encodes a string or bytes to Base64."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return b64.b64encode(data).decode('utf-8')

def base64_decode(data: str) -> str:
    """Decodes a Base64 string to a UTF-8 string."""
    try:
        return b64.b64decode(data).decode('utf-8')
    except (TypeError, b64.binascii.Error):
        return data

def base64_toggle(data: str) -> str:
    """
    Legacy XSStrike logic: encodes if not base64, decodes if it is.
    Note: This is heuristic and can be wrong for some strings.
    """
    if re.match(r'^[A-Za-z0-9+\/=]+$', data) and (len(data) % 4) == 0:
        return base64_decode(data)
    else:
        return base64_encode(data)

# Legacy alias
base64 = base64_toggle
