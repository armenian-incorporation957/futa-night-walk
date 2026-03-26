from __future__ import annotations

import json
from pathlib import Path

from game.models.definitions import SkillDef


REQUIRED_KEYS = {
    "id",
    "name",
    "description",
    "group",
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
        duration = float(raw.get("duration", 1.6))
        shots = int(raw.get("shots", 1))
        spread_angle = float(raw.get("spread_angle", 18.0))
        burn_duration = float(raw.get("burn_duration", 0.0))
        burn_damage = float(raw.get("burn_damage", 0.0))
        slow_factor = float(raw.get("slow_factor", 1.0))
        slow_duration = float(raw.get("slow_duration", 0.0))
        chain_targets = int(raw.get("chain_targets", 0))
        chain_range = float(raw.get("chain_range", 0.0))
        chain_damage_ratio = float(raw.get("chain_damage_ratio", 0.0))
        explosion_radius = float(raw.get("explosion_radius", 0.0))
        explosion_damage_ratio = float(raw.get("explosion_damage_ratio", 0.0))
        orbit_count = int(raw.get("orbit_count", 0))
        orbit_radius = float(raw.get("orbit_radius", 0.0))
        orbit_speed = float(raw.get("orbit_speed", 0.0))
        homing_strength = float(raw.get("homing_strength", 0.0))
        hit_stun = float(raw.get("hit_stun", 0.0))
        healing_amount = float(raw.get("healing_amount", 0.0))
        raw_level_scaling = raw.get("level_scaling", {})
        if not isinstance(raw_level_scaling, dict):
            raise ValueError(f"Skill '{skill_id}' has invalid level_scaling")
        level_scaling: dict[int, dict[str, int | float]] = {}
        for level_key, overrides in raw_level_scaling.items():
            level = int(level_key)
            if level < 2 or level > 3 or not isinstance(overrides, dict):
                raise ValueError(f"Skill '{skill_id}' has invalid level scaling entry")
            level_scaling[level] = {
                str(key): value
                for key, value in overrides.items()
                if isinstance(value, (int, float))
            }
        if (
            cooldown <= 0
            or damage <= 0
            or projectile_speed < 0
            or duration <= 0
            or shots <= 0
            or burn_duration < 0
            or burn_damage < 0
            or slow_factor <= 0
            or slow_duration < 0
            or chain_targets < 0
            or chain_range < 0
            or chain_damage_ratio < 0
            or explosion_radius < 0
            or explosion_damage_ratio < 0
            or orbit_count < 0
            or orbit_radius < 0
            or homing_strength < 0
            or hit_stun < 0
            or healing_amount < 0
        ):
            raise ValueError(f"Skill '{skill_id}' has invalid numeric values")

        skills[skill_id] = SkillDef(
            id=skill_id,
            name=str(raw["name"]),
            description=str(raw["description"]),
            group=str(raw["group"]),
            cooldown=cooldown,
            damage=damage,
            projectile_speed=projectile_speed,
            behavior_type=str(raw["behavior_type"]),
            level_scaling=level_scaling,
            duration=duration,
            shots=shots,
            spread_angle=spread_angle,
            burn_duration=burn_duration,
            burn_damage=burn_damage,
            slow_factor=slow_factor,
            slow_duration=slow_duration,
            chain_targets=chain_targets,
            chain_range=chain_range,
            chain_damage_ratio=chain_damage_ratio,
            explosion_radius=explosion_radius,
            explosion_damage_ratio=explosion_damage_ratio,
            orbit_count=orbit_count,
            orbit_radius=orbit_radius,
            orbit_speed=orbit_speed,
            homing_strength=homing_strength,
            hit_stun=hit_stun,
            healing_amount=healing_amount,
        )

    return skills
