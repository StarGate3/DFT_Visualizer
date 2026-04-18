"""Project save/load for DFT Visualizer .dftviz files."""
from __future__ import annotations

import dataclasses
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from src.data.models import (
    CompoundFranckCondon,
    CompoundHomoLumo,
    CompoundStates,
    DFTDataset,
)

logger = logging.getLogger(__name__)

_VERSION = "1.0"
_APP_VERSION = "0.1.0"


def save_project(
    filepath: Path,
    dataset: DFTDataset,
    style: dict,
    ui_state: dict,
) -> None:
    """Serialize full app state to *filepath* as a .dftviz JSON file."""
    import copy

    style_copy = copy.deepcopy(style)
    if "figure" in style_copy and "figsize" in style_copy["figure"]:
        style_copy["figure"]["figsize"] = list(style_copy["figure"]["figsize"])

    payload = {
        "version": _VERSION,
        "app_version": _APP_VERSION,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "data": {
            "homo_lumo": [dataclasses.asdict(e) for e in dataset.homo_lumo],
            "states": [dataclasses.asdict(e) for e in dataset.states],
            "franck_condon": [dataclasses.asdict(e) for e in dataset.franck_condon],
        },
        "style": style_copy,
        "ui_state": ui_state,
    }
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    logger.info("Project saved to %s", filepath)


def load_project(filepath: Path) -> tuple[DFTDataset, dict, dict]:
    """Load a .dftviz file.

    Returns:
        (dataset, style, ui_state)

    Raises:
        ValueError: If the file is malformed or uses an incompatible version.
    """
    with filepath.open(encoding="utf-8") as fh:
        raw = json.load(fh)

    if not isinstance(raw, dict):
        raise ValueError("Invalid .dftviz file: root must be a JSON object.")
    version = raw.get("version", "")
    if version != _VERSION:
        raise ValueError(
            f"Incompatible project version '{version}'. Expected '{_VERSION}'."
        )

    # Reconstruct dataset
    data = raw.get("data", {})
    try:
        homo_lumo = [CompoundHomoLumo(**e) for e in data.get("homo_lumo", [])]
        states = [CompoundStates(**e) for e in data.get("states", [])]
        franck_condon = [CompoundFranckCondon(**e) for e in data.get("franck_condon", [])]
    except (TypeError, KeyError) as exc:
        raise ValueError(f"Malformed data section: {exc}") from exc
    dataset = DFTDataset(homo_lumo=homo_lumo, states=states, franck_condon=franck_condon)

    # Fix non-JSON types in style
    style = raw.get("style", {})
    if "figure" in style and "figsize" in style["figure"]:
        style["figure"]["figsize"] = tuple(style["figure"]["figsize"])

    ui_state = raw.get("ui_state", {})
    logger.info("Project loaded from %s", filepath)
    return dataset, style, ui_state
