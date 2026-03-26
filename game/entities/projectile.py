from __future__ import annotations

import math

from game.core.pygame_support import require_pygame
from game.entities.base import Entity
from game.models.definitions import SkillDef


class Projectile(Entity):
    def __init__(
        self,
        x: float,
        y: float,
        direction: tuple[float, float],
        speed: float,
        skill: SkillDef,
        lifetime: float | None,
        color: tuple[int, int, int],
        owner_faction: str,
        angle: float = 0.0,
        uses_lifetime: bool = True,
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
        self.damage = skill.damage
        self.skill = skill
        self.lifetime = lifetime if lifetime is not None else skill.duration
        self.uses_lifetime = uses_lifetime
        self.owner_skill = skill.id
        self.angle = angle
        self.hit_cooldowns: dict[int, float] = {}

    def update(self, dt: float, player=None, enemies: list | None = None) -> None:
        if self.skill.behavior_type == "orbit_guard" and player is not None:
            self.angle += self.skill.orbit_speed * dt
            self.x = player.x + math.cos(self.angle) * self.skill.orbit_radius
            self.y = player.y + math.sin(self.angle) * self.skill.orbit_radius
        else:
            if self.skill.homing_strength > 0 and enemies:
                living_enemies = [enemy for enemy in enemies if enemy.is_alive()]
                if living_enemies:
                    target = min(
                        living_enemies,
                        key=lambda enemy: (enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2,
                    )
                    desired_dx = target.x - self.x
                    desired_dy = target.y - self.y
                    desired_length = math.hypot(desired_dx, desired_dy) or 1.0
                    desired_vx = desired_dx / desired_length * self.skill.projectile_speed
                    desired_vy = desired_dy / desired_length * self.skill.projectile_speed
                    turn = min(1.0, self.skill.homing_strength * dt / max(self.skill.projectile_speed, 1.0))
                    self.vx += (desired_vx - self.vx) * turn
                    self.vy += (desired_vy - self.vy) * turn
            super().update(dt)

        if self.uses_lifetime:
            self.lifetime -= dt
            if self.lifetime <= 0:
                self.alive = False
        for target_id in list(self.hit_cooldowns):
            self.hit_cooldowns[target_id] = max(0.0, self.hit_cooldowns[target_id] - dt)
            if self.hit_cooldowns[target_id] == 0:
                del self.hit_cooldowns[target_id]

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
