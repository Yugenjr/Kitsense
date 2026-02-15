from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

DATA_PATH = Path(__file__).with_name("kits_data.json")


class KitNotFoundError(LookupError):
    """Raised when a kit_id does not exist in the repository."""


@lru_cache(maxsize=1)
def load_kits_data() -> Dict[str, Any]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload


def _normalized_kit_index() -> Dict[str, str]:
    kits_by_id = load_kits_data().get("kits_by_id", {})
    return {kit_id.upper(): kit_id for kit_id in kits_by_id.keys()}


def get_kit_by_id(kit_id: str) -> Dict[str, Any]:
    """Return one exact kit using a case-insensitive kit_id lookup.

    Rules:
    - exact match only (no partial matching)
    - case-insensitive
    - raise clear error when missing
    """
    token = (kit_id or "").strip().upper()
    kit_index = _normalized_kit_index()

    canonical_id = kit_index.get(token)
    if canonical_id is None:
        raise KitNotFoundError("Kit not found")

    return load_kits_data()["kits_by_id"][canonical_id]


def get_kit_by_identifier(identifier: str) -> Optional[Dict[str, Any]]:
    """Resolve by kit_id first, then exact order_id (case-insensitive)."""
    try:
        return get_kit_by_id(identifier)
    except KitNotFoundError:
        token = (identifier or "").strip().upper()
        for kit in load_kits_data().get("kits_by_id", {}).values():
            if token in {order_id.upper() for order_id in kit.get("order_ids", [])}:
                return kit
    return None
