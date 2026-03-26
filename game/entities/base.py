from __future__ import annotations

from dataclasses import dataclass

from game.core.pygame_support import require_pygame


@dataclass
class Entity:
    x: float
    y: float
    radius: float
    color: tuple[int, int, int]
    vx: float = 0.0
    vy: float = 0.0
    hp: float = 1.0
    max_hp: float = 1.0
    faction: str = "neutral"
    alive: bool = True

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surface) -> None:
        pygame = require_pygame()
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x), int(self.y)),
            int(self.radius),
        )

    def take_damage(self, amount: float) -> None:
        if amount <= 0:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

    def is_alive(self) -> bool:
        return self.alive and self.hp > 0
