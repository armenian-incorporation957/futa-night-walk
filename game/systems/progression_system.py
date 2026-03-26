from __future__ import annotations

import random
from dataclasses import replace

from game.entities.player import Player
from game.models.definitions import SkillDef


class ProgressionSystem:
    def __init__(self, skill_defs: dict[str, SkillDef], rng: random.Random | None = None) -> None:
        self.skill_defs = skill_defs
        self.rng = rng or random.Random()
        self.skill_groups = self._build_groups()
        self._cycle_stage_pools: dict[int, list[list[str]]] = {}

    def grant_exp(self, player: Player, amount: int) -> bool:
        if amount <= 0:
            return False

        player.exp += amount
        leveled_up = False
        while player.exp >= player.exp_to_next:
            player.exp -= player.exp_to_next
            player.level += 1
            player.exp_to_next = self._exp_to_next(player.level)
            leveled_up = True
        return leveled_up

    def build_cycle_stage_pools(self, cycle: int) -> list[list[str]]:
        if cycle not in self._cycle_stage_pools:
            group_items = list(self.skill_groups.items())
            self.rng.shuffle(group_items)
            self._cycle_stage_pools[cycle] = [list(skill_ids) for _, skill_ids in group_items]
        return [list(pool) for pool in self._cycle_stage_pools[cycle]]

    def get_stage_skill_pool(self, stage_index: int) -> list[str]:
        cycle = ((stage_index - 1) // 4) + 1
        local_stage = ((stage_index - 1) % 4)
        pools = self.build_cycle_stage_pools(cycle)
        return list(pools[local_stage])

    def build_upgrade_choices(
        self,
        stage_skill_pool: list[str],
        stage_skill_levels: dict[str, int],
        count: int = 3,
    ) -> list[str]:
        available = [skill_id for skill_id in stage_skill_pool if stage_skill_levels.get(skill_id, 0) < 3]
        if not available:
            return []

        shuffled = list(available)
        self.rng.shuffle(shuffled)
        return shuffled[: min(count, len(shuffled))]

    def apply_upgrade(
        self,
        player: Player,
        skill_id: str,
        stage_skill_levels: dict[str, int],
    ) -> int:
        if skill_id not in self.skill_defs:
            raise ValueError(f"Unknown skill '{skill_id}'")

        current_level = stage_skill_levels.get(skill_id, 0)
        if current_level >= 3:
            raise ValueError(f"Skill '{skill_id}' already maxed")

        new_level = current_level + 1
        stage_skill_levels[skill_id] = new_level
        player.skill_levels[skill_id] = new_level
        if new_level == 1 and skill_id not in player.owned_skills:
            player.owned_skills.append(skill_id)
            player.skill_timers.setdefault(skill_id, 0.0)
        return new_level

    def all_stage_skills_maxed(
        self,
        stage_skill_pool: list[str],
        stage_skill_levels: dict[str, int],
    ) -> bool:
        return bool(stage_skill_pool) and all(stage_skill_levels.get(skill_id, 0) >= 3 for skill_id in stage_skill_pool)

    def effective_skill_defs(self, skill_levels: dict[str, int]) -> dict[str, SkillDef]:
        result: dict[str, SkillDef] = {}
        for skill_id, level in skill_levels.items():
            if level <= 0 or skill_id not in self.skill_defs:
                continue
            result[skill_id] = self._skill_at_level(self.skill_defs[skill_id], level)
        return result

    def reset_stage_progress(self, player: Player) -> None:
        player.level = 1
        player.exp = 0
        player.exp_to_next = self._exp_to_next(1)
        player.owned_skills.clear()
        player.skill_levels.clear()
        player.skill_timers.clear()

    def _skill_at_level(self, skill: SkillDef, level: int) -> SkillDef:
        effective = skill
        for current_level in range(2, min(level, 3) + 1):
            overrides = skill.level_scaling.get(current_level, {})
            if overrides:
                effective = replace(effective, **overrides)
        return effective

    def _build_groups(self) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = {}
        for skill in self.skill_defs.values():
            groups.setdefault(skill.group, []).append(skill.id)
        return dict(sorted(groups.items()))

    def _exp_to_next(self, level: int) -> int:
        return 20 + (level - 1) * 12
