from __future__ import annotations

import math

from game.entities.enemy import Enemy
from game.entities.player import Player


class MovementSystem:
    def update_enemies(
        self,
        enemies: list[Enemy],
        player: Player,
        dt: float,
        bounds: tuple[float, float, float, float],
    ) -> None:
        min_x, min_y, max_x, max_y = bounds
        for enemy in enemies:
            if not enemy.is_alive():
                continue

            dx = player.x - enemy.x
            dy = player.y - enemy.y
            length = math.hypot(dx, dy) or 1.0

            if enemy.ai_type == "orbit" and length < 120:
                enemy.vx = -dy / length * enemy.speed
                enemy.vy = dx / length * enemy.speed
            else:
                enemy.vx = dx / length * enemy.speed
                enemy.vy = dy / length * enemy.speed

            enemy.update(dt)
            enemy.x = min(max(enemy.x, min_x + enemy.radius), max_x - enemy.radius)
            enemy.y = min(max(enemy.y, min_y + enemy.radius), max_y - enemy.radius)
