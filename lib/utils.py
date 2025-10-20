## lib/utils.py

import json
from typing import Any, Dict


def to_json_str(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)


def from_json_str(s: str) -> Dict[str, Any]:
    try:
        return json.loads(s) if s else {}
    except Exception:
        return {}
