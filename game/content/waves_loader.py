from __future__ import annotations

import json
from pathlib import Path

from game.models.definitions import WaveDef


REQUIRED_KEYS = {"stage", "time", "enemy_id", "count", "interval"}


def load_waves(path: str | Path) -> list[WaveDef]:
    raw_items = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw_items, list):
        raise ValueError("Wave data must be a list.")

    waves: list[WaveDef] = []
    for raw in raw_items:
        if not REQUIRED_KEYS.issubset(raw):
            missing = sorted(REQUIRED_KEYS - set(raw))
            raise ValueError(f"Wave definition missing keys: {missing}")

        stage = int(raw["stage"])
        time = float(raw["time"])
        count = int(raw["count"])
        interval = float(raw["interval"])
        if stage <= 0 or time < 0 or count <= 0 or interval < 0:
            raise ValueError("Wave definition has invalid numeric values")

        waves.append(
            WaveDef(
                stage=stage,
                time=time,
                enemy_id=str(raw["enemy_id"]),
                count=count,
                interval=interval,
            )
        )

    return sorted(waves, key=lambda wave: wave.time)
