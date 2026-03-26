from __future__ import annotations

import math

from game.core.pygame_support import require_pygame
from game.entities.base import Entity
from game.models.definitions import PlayerStats


class Player(Entity):
    def __init__(self, x: float, y: float, stats: PlayerStats) -> None:
        super().__init__(
            x=x,
            y=y,
            radius=14,
            color=(111, 196, 255),
            hp=float(stats.max_hp),
            max_hp=float(stats.max_hp),
            faction="player",
        )
        self.stats = stats
        self.move_x = 0
        self.move_y = 0
        self.level = 1
        self.exp = 0
        self.exp_to_next = 20
        self.owned_skills: list[str] = []
        self.skill_levels: dict[str, int] = {}
        self.skill_timers: dict[str, float] = {}
        self.hurt_cooldown = 0.0

    def set_movement(self, move_x: int, move_y: int) -> None:
        self.move_x = move_x
        self.move_y = move_y

    def update(self, dt: float, bounds: tuple[float, float, float, float] | None = None) -> None:
        length = math.hypot(self.move_x, self.move_y)
        if length > 0:
            self.vx = self.move_x / length * self.stats.move_speed
            self.vy = self.move_y / length * self.stats.move_speed
        else:
            self.vx = 0
            self.vy = 0

        super().update(dt)

        if bounds is not None:
            min_x, min_y, max_x, max_y = bounds
            self.x = min(max(self.x, min_x + self.radius), max_x - self.radius)
            self.y = min(max(self.y, min_y + self.radius), max_y - self.radius)

        for skill_id in list(self.skill_timers):
            self.skill_timers[skill_id] = max(0.0, self.skill_timers[skill_id] - dt)
        self.hurt_cooldown = max(0.0, self.hurt_cooldown - dt)

    def draw(self, surface) -> None:
        pygame = require_pygame()
        super().draw(surface)
        pygame.draw.circle(
            surface,
            (235, 247, 255),
            (int(self.x), int(self.y)),
            int(self.radius),
            2,
        )
