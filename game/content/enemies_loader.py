from __future__ import annotations

import json
from pathlib import Path

from game.models.definitions import EnemyDef


REQUIRED_KEYS = {
    "id",
    "name",
    "hp",
    "speed",
    "contact_damage",
    "sprite_key",
    "ai_type",
}


def load_enemies(path: str | Path) -> dict[str, EnemyDef]:
    raw_items = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw_items, list):
        raise ValueError("Enemy data must be a list.")

    enemies: dict[str, EnemyDef] = {}
    for raw in raw_items:
        if not REQUIRED_KEYS.issubset(raw):
            missing = sorted(REQUIRED_KEYS - set(raw))
            raise ValueError(f"Enemy definition missing keys: {missing}")

        enemy_id = str(raw["id"])
        if enemy_id in enemies:
            raise ValueError(f"Duplicate enemy id '{enemy_id}'")

        hp = int(raw["hp"])
        speed = float(raw["speed"])
        damage = int(raw["contact_damage"])
        exp_reward = int(raw.get("exp_reward", 5))
        if hp <= 0 or speed <= 0 or damage <= 0 or exp_reward <= 0:
            raise ValueError(f"Enemy '{enemy_id}' has invalid numeric values")

        enemies[enemy_id] = EnemyDef(
            id=enemy_id,
            name=str(raw["name"]),
            hp=hp,
            speed=speed,
            contact_damage=damage,
            sprite_key=str(raw["sprite_key"]),
            ai_type=str(raw["ai_type"]),
            exp_reward=exp_reward,
        )

    return enemies
