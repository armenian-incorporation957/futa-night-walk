from __future__ import annotations

from game.core.pygame_support import require_pygame
from game.entities.base import Entity


class Pickup(Entity):
    def __init__(self, x: float, y: float, value: int) -> None:
        super().__init__(
            x=x,
            y=y,
            radius=7,
            color=(129, 224, 170),
            hp=1,
            max_hp=1,
            faction="pickup",
        )
        self.value = value
        self.attracted = False
        self.attract_speed = 0.0

    def draw(self, surface) -> None:
        pygame = require_pygame()
        points = [
            (int(self.x), int(self.y - self.radius)),
            (int(self.x + self.radius), int(self.y)),
            (int(self.x), int(self.y + self.radius)),
            (int(self.x - self.radius), int(self.y)),
        ]
        pygame.draw.polygon(surface, self.color, points)
