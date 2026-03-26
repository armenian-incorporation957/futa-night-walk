from __future__ import annotations

import math

from game.core.collision import circles_overlap
from game.entities.enemy import Enemy
from game.entities.pickup import Pickup
from game.entities.player import Player
from game.entities.projectile import Projectile
from game.models.definitions import SkillDef


SKILL_COLORS = {
    "fire_talisman": (255, 135, 92),
    "thunder_mark": (255, 240, 135),
    "frost_sand": (133, 209, 255),
    "spirit_orb": (198, 157, 255),
    "ward_shard": (156, 245, 214),
}


class CombatSystem:
    def spawn_player_projectiles(
        self,
        player: Player,
        skill_defs: dict[str, SkillDef],
        enemies: list[Enemy],
    ) -> list[Projectile]:
        if not player.owned_skills:
            return []

        projectiles: list[Projectile] = []
        aim_direction = self._aim_direction(player, enemies)

        for skill_id in player.owned_skills:
            if player.skill_timers.get(skill_id, 0.0) > 0.0:
                continue

            skill = skill_defs[skill_id]
            directions = self._build_directions(aim_direction, skill)
            color = SKILL_COLORS.get(skill_id, (255, 255, 255))
            for direction in directions:
                projectiles.append(
                    Projectile(
                        x=player.x,
                        y=player.y,
                        direction=direction,
                        speed=skill.projectile_speed,
                        damage=skill.damage,
                        lifetime=1.6,
                        color=color,
                        owner_skill=skill.id,
                        owner_faction=player.faction,
                    )
                )
            player.skill_timers[skill_id] = skill.cooldown

        return projectiles

    def update_projectiles(
        self,
        projectiles: list[Projectile],
        dt: float,
        bounds: tuple[float, float, float, float],
    ) -> None:
        min_x, min_y, max_x, max_y = bounds
        for projectile in projectiles:
            projectile.update(dt)
            if (
                projectile.x < min_x - 24
                or projectile.x > max_x + 24
                or projectile.y < min_y - 24
                or projectile.y > max_y + 24
            ):
                projectile.alive = False

    def resolve(
        self,
        projectiles: list[Projectile],
        enemies: list[Enemy],
        pickups: list[Pickup],
        player: Player,
    ) -> int:
        gained_exp = 0

        for projectile in projectiles:
            if not projectile.is_alive():
                continue
            for enemy in enemies:
                if not enemy.is_alive():
                    continue
                if circles_overlap(projectile, enemy):
                    enemy.take_damage(projectile.damage)
                    projectile.alive = False
                    if not enemy.is_alive():
                        pickups.append(Pickup(enemy.x, enemy.y, enemy.exp_reward))
                    break

        for enemy in enemies:
            if enemy.is_alive() and circles_overlap(enemy, player):
                player.take_damage(max(1, enemy.contact_damage - player.stats.contact_armor))
                enemy.alive = False
                pickups.append(Pickup(enemy.x, enemy.y, enemy.exp_reward))

        for pickup in pickups:
            if pickup.is_alive() and circles_overlap(pickup, player):
                gained_exp += pickup.value
                pickup.alive = False

        return gained_exp

    def _aim_direction(self, player: Player, enemies: list[Enemy]) -> tuple[float, float]:
        living_enemies = [enemy for enemy in enemies if enemy.is_alive()]
        if not living_enemies:
            return (0.0, -1.0)

        nearest = min(
            living_enemies,
            key=lambda enemy: (enemy.x - player.x) ** 2 + (enemy.y - player.y) ** 2,
        )
        return (nearest.x - player.x, nearest.y - player.y)

    def _build_directions(
        self,
        aim_direction: tuple[float, float],
        skill: SkillDef,
    ) -> list[tuple[float, float]]:
        if skill.behavior_type == "spread" and skill.shots > 1:
            base_angle = math.atan2(aim_direction[1], aim_direction[0])
            mid = (skill.shots - 1) / 2
            directions = []
            for index in range(skill.shots):
                offset = math.radians((index - mid) * skill.spread_angle)
                angle = base_angle + offset
                directions.append((math.cos(angle), math.sin(angle)))
            return directions

        return [aim_direction]
