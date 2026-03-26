from __future__ import annotations

import random
from dataclasses import dataclass

from game.entities.enemy import Enemy
from game.models.definitions import EnemyDef, WaveDef


@dataclass
class _WaveTracker:
    definition: WaveDef
    spawned: int = 0


class SpawnSystem:
    def __init__(self, waves: list[WaveDef], rng: random.Random | None = None) -> None:
        self.trackers = [_WaveTracker(definition=wave) for wave in sorted(waves, key=lambda item: item.time)]
        self.rng = rng or random.Random()

    def update(
        self,
        current_time: float,
        enemy_defs: dict[str, EnemyDef],
        bounds: tuple[float, float, float, float],
    ) -> list[Enemy]:
        spawned: list[Enemy] = []
        for tracker in self.trackers:
            wave = tracker.definition
            while tracker.spawned < wave.count:
                due_time = wave.time + tracker.spawned * wave.interval
                if current_time < due_time:
                    break

                if wave.enemy_id not in enemy_defs:
                    raise ValueError(f"Wave references unknown enemy '{wave.enemy_id}'")

                spawn_x, spawn_y = self._spawn_position(bounds)
                spawned.append(Enemy(enemy_defs[wave.enemy_id], spawn_x, spawn_y))
                tracker.spawned += 1
        return spawned

    def _spawn_position(self, bounds: tuple[float, float, float, float]) -> tuple[float, float]:
        min_x, min_y, max_x, max_y = bounds
        edge = self.rng.choice(("top", "right", "bottom", "left"))
        if edge == "top":
            return (self.rng.uniform(min_x, max_x), min_y)
        if edge == "right":
            return (max_x, self.rng.uniform(min_y, max_y))
        if edge == "bottom":
            return (self.rng.uniform(min_x, max_x), max_y)
        return (min_x, self.rng.uniform(min_y, max_y))
