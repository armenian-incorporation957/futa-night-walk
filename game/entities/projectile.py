from __future__ import annotations

import math

from game.core.pygame_support import require_pygame
from game.entities.base import Entity


class Projectile(Entity):
    def __init__(
        self,
        x: float,
        y: float,
        direction: tuple[float, float],
        speed: float,
        damage: int,
        lifetime: float,
        color: tuple[int, int, int],
        owner_skill: str,
        owner_faction: str,
    ) -> None:
        dx, dy = direction
        length = math.hypot(dx, dy) or 1.0
        super().__init__(
            x=x,
            y=y,
            radius=6,
            color=color,
            vx=dx / length * speed,
            vy=dy / length * speed,
            hp=1,
            max_hp=1,
            faction=owner_faction,
        )
        self.damage = damage
        self.lifetime = lifetime
        self.owner_skill = owner_skill

    def update(self, dt: float) -> None:
        super().update(dt)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface) -> None:
        pygame = require_pygame()
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (int(self.x), int(self.y)),
            int(self.radius),
            1,
        )
