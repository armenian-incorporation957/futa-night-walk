from __future__ import annotations

import random

from game.entities.player import Player
from game.models.definitions import SkillDef


class ProgressionSystem:
    def __init__(self, skill_defs: dict[str, SkillDef], rng: random.Random | None = None) -> None:
        self.skill_defs = skill_defs
        self.rng = rng or random.Random()

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

    def build_upgrade_choices(self, player: Player, count: int = 3) -> list[str]:
        available = [skill_id for skill_id in self.skill_defs if skill_id not in player.owned_skills]
        if not available:
            return []

        shuffled = list(available)
        self.rng.shuffle(shuffled)
        return shuffled[: min(count, len(shuffled))]

    def apply_upgrade(self, player: Player, skill_id: str) -> None:
        if skill_id not in self.skill_defs:
            raise ValueError(f"Unknown skill '{skill_id}'")
        if skill_id in player.owned_skills:
            raise ValueError(f"Skill '{skill_id}' already selected")

        player.owned_skills.append(skill_id)
        player.skill_timers.setdefault(skill_id, 0.0)

    def _exp_to_next(self, level: int) -> int:
        return 20 + (level - 1) * 12
