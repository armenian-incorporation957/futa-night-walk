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
        self.active_enemy_count = 0
        self.script_end_time = max(
            (wave.time + (wave.count - 1) * wave.interval for wave in waves),
            default=0.0,
        )
        self.next_director_spawn_time = self.script_end_time

    def set_active_enemy_count(self, count: int) -> None:
        self.active_enemy_count = max(0, count)

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

        if current_time >= self.script_end_time:
            projected_count = self.active_enemy_count + len(spawned)
            while current_time >= self.next_director_spawn_time:
                soft_cap = 6 + min(10, int(current_time // 20) * 2)
                if projected_count >= soft_cap:
                    self.next_director_spawn_time = current_time + 0.35
                    break

                spawn_budget = 1 + int(current_time >= 45) + int(current_time >= 90)
                for _ in range(spawn_budget):
                    if projected_count >= soft_cap:
                        break
                    enemy_id = self._director_enemy_id(current_time, enemy_defs)
                    spawn_x, spawn_y = self._spawn_position(bounds)
                    spawned.append(Enemy(enemy_defs[enemy_id], spawn_x, spawn_y))
                    projected_count += 1

                self.next_director_spawn_time += self._director_interval(current_time)
        return spawned

    def _director_interval(self, current_time: float) -> float:
        return max(0.45, 1.1 - current_time * 0.006)

    def _director_enemy_id(self, current_time: float, enemy_defs: dict[str, EnemyDef]) -> str:
        candidates: list[tuple[str, float]] = [("paper_spirit", 1.0), ("lantern_wisp", 0.55)]
        if current_time >= 25:
            candidates.append(("mist_fox", 0.3 if current_time < 60 else 0.65))

        available = [(enemy_id, weight) for enemy_id, weight in candidates if enemy_id in enemy_defs]
        total_weight = sum(weight for _, weight in available)
        roll = self.rng.uniform(0.0, total_weight)
        cumulative = 0.0
        for enemy_id, weight in available:
            cumulative += weight
            if roll <= cumulative:
                return enemy_id
        return available[-1][0]

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
