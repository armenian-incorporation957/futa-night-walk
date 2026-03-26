from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GameConfig:
    width: int = 960
    height: int = 540
    title: str = "\u7b26\u5854\u591c\u884c"
    target_fps: int = 60
    background_color: tuple[int, int, int] = (14, 18, 24)
    grid_color: tuple[int, int, int] = (24, 30, 40)
    player_spawn: tuple[float, float] = (480.0, 270.0)
    arena_padding: int = 24
    data_dir: Path = Path(__file__).resolve().parents[2] / "assets" / "data"
