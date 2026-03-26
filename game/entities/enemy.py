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
        self.burn_timer = 0.0
        self.burn_damage = 0.0
        self.slow_timer = 0.0
        self.slow_factor = 1.0
        self.stun_timer = 0.0
        self.drop_spawned = False

    def apply_burn(self, damage_per_second: float, duration: float) -> None:
        if duration <= 0 or damage_per_second <= 0:
            return
        self.burn_timer = max(self.burn_timer, duration)
        self.burn_damage = max(self.burn_damage, damage_per_second)

    def apply_slow(self, factor: float, duration: float) -> None:
        if duration <= 0:
            return
        self.slow_timer = max(self.slow_timer, duration)
        self.slow_factor = min(self.slow_factor, factor)

    def apply_stun(self, duration: float) -> None:
        if duration <= 0:
            return
        self.stun_timer = max(self.stun_timer, duration)

    def update_status(self, dt: float) -> None:
        if self.burn_timer > 0:
            self.take_damage(self.burn_damage * dt)
            self.burn_timer = max(0.0, self.burn_timer - dt)
            if self.burn_timer == 0:
                self.burn_damage = 0.0

        if self.slow_timer > 0:
            self.slow_timer = max(0.0, self.slow_timer - dt)
            if self.slow_timer == 0:
                self.slow_factor = 1.0

        if self.stun_timer > 0:
            self.stun_timer = max(0.0, self.stun_timer - dt)

    @property
    def current_speed(self) -> float:
        if self.stun_timer > 0:
            return 0.0
        return self.speed * self.slow_factor

    def draw(self, surface) -> None:
        if self.burn_timer > 0:
            self.color = (255, 118, 92)
        elif self.slow_timer > 0:
            self.color = (138, 210, 255)
        else:
            self.color = ENEMY_COLORS.get(self.definition.sprite_key, (210, 90, 110))
        super().draw(surface)
