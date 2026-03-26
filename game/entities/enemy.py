from __future__ import annotations

from game.entities.base import Entity
from game.models.definitions import EnemyDef


ENEMY_COLORS = {
    "paper_spirit": (229, 223, 190),
    "lantern_wisp": (255, 171, 95),
    "mist_fox": (110, 190, 255),
}


class Enemy(Entity):
    def __init__(self, definition: EnemyDef, x: float, y: float) -> None:
        color = ENEMY_COLORS.get(definition.sprite_key, (210, 90, 110))
        super().__init__(
            x=x,
            y=y,
            radius=12,
            color=color,
            hp=float(definition.hp),
            max_hp=float(definition.hp),
            faction="enemy",
        )
        self.definition = definition
        self.speed = definition.speed
        self.contact_damage = definition.contact_damage
        self.ai_type = definition.ai_type
        self.exp_reward = definition.exp_reward
