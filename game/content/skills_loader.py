from __future__ import annotations

import json
from pathlib import Path

from game.models.definitions import SkillDef


REQUIRED_KEYS = {
    "id",
    "name",
    "cooldown",
    "damage",
    "projectile_speed",
    "behavior_type",
}


def load_skills(path: str | Path) -> dict[str, SkillDef]:
    raw_items = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw_items, list):
        raise ValueError("Skill data must be a list.")

    skills: dict[str, SkillDef] = {}
    for raw in raw_items:
        if not REQUIRED_KEYS.issubset(raw):
            missing = sorted(REQUIRED_KEYS - set(raw))
            raise ValueError(f"Skill definition missing keys: {missing}")

        skill_id = str(raw["id"])
        if skill_id in skills:
            raise ValueError(f"Duplicate skill id '{skill_id}'")

        cooldown = float(raw["cooldown"])
        damage = int(raw["damage"])
        projectile_speed = float(raw["projectile_speed"])
        shots = int(raw.get("shots", 1))
        spread_angle = float(raw.get("spread_angle", 18.0))
        if cooldown <= 0 or damage <= 0 or projectile_speed <= 0 or shots <= 0:
            raise ValueError(f"Skill '{skill_id}' has invalid numeric values")

        skills[skill_id] = SkillDef(
            id=skill_id,
            name=str(raw["name"]),
            cooldown=cooldown,
            damage=damage,
            projectile_speed=projectile_speed,
            behavior_type=str(raw["behavior_type"]),
            shots=shots,
            spread_angle=spread_angle,
        )

    return skills
