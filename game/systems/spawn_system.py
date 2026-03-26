from __future__ import annotations

import random
from dataclasses import dataclass, replace

from game.entities.enemy import Enemy
from game.models.definitions import EnemyDef, WaveDef


@dataclass
class _WaveTracker:
    definition: WaveDef
    spawned: int = 0


class SpawnSystem:
    DIRECTOR_PROFILES = {
        1: {"weights": {"paper_spirit": 1.0, "lantern_wisp": 0.25}, "interval": 1.05, "soft_cap": 7, "burst": 1},
        2: {"weights": {"paper_spirit": 0.7, "lantern_wisp": 1.0}, "interval": 0.88, "soft_cap": 8, "burst": 1},
        3: {"weights": {"paper_spirit": 0.55, "lantern_wisp": 0.8, "mist_fox": 0.75}, "interval": 0.76, "soft_cap": 9, "burst": 2},
        4: {"weights": {"paper_spirit": 0.6, "lantern_wisp": 1.0, "mist_fox": 1.0}, "interval": 0.62, "soft_cap": 10, "burst": 2},
    }

    def __init__(self, waves: list[WaveDef], rng: random.Random | None = None) -> None:
        self.all_waves = list(waves)
        self.rng = rng or random.Random()
        self.active_enemy_count = 0
        self.stage_pattern = 1
        self.difficulty_multiplier = 1.0
        self.trackers: list[_WaveTracker] = []
        self.script_end_time = 0.0
        self.next_director_spawn_time = 0.0
        self.configure_stage(stage_pattern=1, difficulty_multiplier=1.0)

    def configure_stage(self, stage_pattern: int, difficulty_multiplier: float) -> None:
        self.stage_pattern = stage_pattern
        self.difficulty_multiplier = difficulty_multiplier
        stage_waves = [wave for wave in self.all_waves if wave.stage == stage_pattern]
        self.trackers = [_WaveTracker(definition=wave) for wave in sorted(stage_waves, key=lambda item: item.time)]
        self.script_end_time = max(
            (wave.time + (wave.count - 1) * wave.interval for wave in stage_waves),
            default=0.0,
        )
        self.next_director_spawn_time = self.script_end_time + 0.2

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
                spawned.append(Enemy(self._scaled_enemy_def(enemy_defs[wave.enemy_id]), spawn_x, spawn_y))
                tracker.spawned += 1

        if current_time >= self.script_end_time:
            projected_count = self.active_enemy_count + len(spawned)
            director_profile = self.DIRECTOR_PROFILES[self.stage_pattern]
            soft_cap = director_profile["soft_cap"] + max(0, int(round((self.difficulty_multiplier - 1.0) / 0.06)))
            burst = director_profile["burst"]
            while current_time >= self.next_director_spawn_time:
                if projected_count >= soft_cap:
                    self.next_director_spawn_time = current_time + 0.25
                    break

                for _ in range(burst):
                    if projected_count >= soft_cap:
                        break
                    enemy_id = self._director_enemy_id(enemy_defs)
                    spawn_x, spawn_y = self._spawn_position(bounds)
                    spawned.append(Enemy(self._scaled_enemy_def(enemy_defs[enemy_id]), spawn_x, spawn_y))
                    projected_count += 1

                self.next_director_spawn_time += self._director_interval()
        return spawned

    def _director_interval(self) -> float:
        base_interval = self.DIRECTOR_PROFILES[self.stage_pattern]["interval"]
        reduction = max(0.55, 1.0 - max(0.0, self.difficulty_multiplier - 1.0))
        return max(0.32, base_interval * reduction)

    def _director_enemy_id(self, enemy_defs: dict[str, EnemyDef]) -> str:
        weights = self.DIRECTOR_PROFILES[self.stage_pattern]["weights"]
        available = [(enemy_id, weight) for enemy_id, weight in weights.items() if enemy_id in enemy_defs]
        total_weight = sum(weight for _, weight in available)
        roll = self.rng.uniform(0.0, total_weight)
        cumulative = 0.0
        for enemy_id, weight in available:
            cumulative += weight
            if roll <= cumulative:
                return enemy_id
        return available[-1][0]

    def _scaled_enemy_def(self, enemy_def: EnemyDef) -> EnemyDef:
        hp = max(1, int(round(enemy_def.hp * (1.0 + (self.difficulty_multiplier - 1.0) * 1.6))))
        speed = enemy_def.speed * (1.0 + (self.difficulty_multiplier - 1.0))
        damage = max(1, int(round(enemy_def.contact_damage * (1.0 + (self.difficulty_multiplier - 1.0) * 1.2))))
        return replace(enemy_def, hp=hp, speed=speed, contact_damage=damage)

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
