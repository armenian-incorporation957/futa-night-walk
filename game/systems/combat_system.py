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
        active_projectiles: list[Projectile],
        skill_defs: dict[str, SkillDef],
        enemies: list[Enemy],
    ) -> list[Projectile]:
        if not player.owned_skills:
            return []

        new_projectiles: list[Projectile] = []
        aim_direction = self._aim_direction(player, enemies)

        for skill_id in player.owned_skills:
            if player.skill_timers.get(skill_id, 0.0) > 0.0:
                continue

            skill = skill_defs[skill_id]
            if skill.behavior_type == "orbit_guard":
                active_orbits = [
                    projectile
                    for projectile in active_projectiles
                    if projectile.is_alive() and projectile.owner_skill == skill.id
                ]
                if active_orbits:
                    continue

                orbit_count = max(1, skill.orbit_count)
                for index in range(orbit_count):
                    angle = (math.tau / orbit_count) * index
                    new_projectiles.append(
                        Projectile(
                            x=player.x,
                            y=player.y,
                            direction=(1.0, 0.0),
                            speed=0.0,
                            skill=skill,
                            lifetime=skill.duration,
                            color=SKILL_COLORS.get(skill_id, (255, 255, 255)),
                            owner_faction=player.faction,
                            angle=angle,
                        )
                    )
                player.skill_timers[skill_id] = skill.cooldown
                continue

            directions = self._build_directions(aim_direction, skill)
            color = SKILL_COLORS.get(skill_id, (255, 255, 255))
            for direction in directions:
                new_projectiles.append(
                    Projectile(
                        x=player.x,
                        y=player.y,
                        direction=direction,
                        speed=skill.projectile_speed,
                        skill=skill,
                        lifetime=skill.duration,
                        color=color,
                        owner_faction=player.faction,
                    )
                )
            player.skill_timers[skill_id] = skill.cooldown

        return new_projectiles

    def update_projectiles(
        self,
        projectiles: list[Projectile],
        dt: float,
        bounds: tuple[float, float, float, float],
        player: Player,
        enemies: list[Enemy],
    ) -> None:
        min_x, min_y, max_x, max_y = bounds
        for projectile in projectiles:
            projectile.update(dt, player=player, enemies=enemies)
            if (
                projectile.skill.behavior_type != "orbit_guard"
                and (
                    projectile.x < min_x - 24
                    or projectile.x > max_x + 24
                    or projectile.y < min_y - 24
                    or projectile.y > max_y + 24
                )
            ):
                projectile.alive = False

    def resolve(
        self,
        projectiles: list[Projectile],
        enemies: list[Enemy],
        pickups: list[Pickup],
        player: Player,
    ) -> None:
        for projectile in projectiles:
            if not projectile.is_alive():
                continue
            for enemy in enemies:
                if not enemy.is_alive():
                    continue
                if circles_overlap(projectile, enemy):
                    if projectile.skill.behavior_type == "orbit_guard":
                        target_id = id(enemy)
                        if projectile.hit_cooldowns.get(target_id, 0.0) > 0.0:
                            continue
                        projectile.hit_cooldowns[target_id] = 0.35
                        self._apply_projectile_hit(projectile, enemy, enemies)
                        break

                    self._apply_projectile_hit(projectile, enemy, enemies)
                    projectile.alive = False
                    break

        for enemy in enemies:
            if enemy.is_alive() and circles_overlap(enemy, player) and player.hurt_cooldown <= 0.0:
                player.take_damage(max(1, enemy.contact_damage - player.stats.contact_armor))
                player.hurt_cooldown = 0.55

    def collect_enemy_drops(self, enemies: list[Enemy], pickups: list[Pickup]) -> None:
        for enemy in enemies:
            if enemy.is_alive() or enemy.drop_spawned:
                continue
            pickups.append(Pickup(enemy.x, enemy.y, enemy.exp_reward))
            enemy.drop_spawned = True

    def update_pickups(self, pickups: list[Pickup], player: Player, dt: float) -> int:
        gained_exp = 0
        attract_radius = 120.0
        collect_radius = 24.0

        for pickup in pickups:
            if not pickup.is_alive():
                continue

            dx = player.x - pickup.x
            dy = player.y - pickup.y
            distance = math.hypot(dx, dy)
            if distance <= collect_radius:
                gained_exp += pickup.value
                pickup.alive = False
                continue

            if distance <= attract_radius:
                pickup.attracted = True
                pickup.attract_speed = min(320.0, pickup.attract_speed + 540.0 * dt)
                length = distance or 1.0
                pickup.vx = dx / length * pickup.attract_speed
                pickup.vy = dy / length * pickup.attract_speed
                pickup.update(dt)
            else:
                pickup.attracted = False
                pickup.attract_speed = 0.0
                pickup.vx = 0.0
                pickup.vy = 0.0

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
        if skill.shots > 1:
            base_angle = math.atan2(aim_direction[1], aim_direction[0])
            mid = (skill.shots - 1) / 2
            directions = []
            for index in range(skill.shots):
                offset = math.radians((index - mid) * skill.spread_angle)
                angle = base_angle + offset
                directions.append((math.cos(angle), math.sin(angle)))
            return directions

        return [aim_direction]

    def _apply_projectile_hit(
        self,
        projectile: Projectile,
        primary_enemy: Enemy,
        enemies: list[Enemy],
    ) -> None:
        skill = projectile.skill
        primary_enemy.take_damage(projectile.damage)

        if skill.burn_duration > 0 and skill.burn_damage > 0:
            primary_enemy.apply_burn(skill.burn_damage, skill.burn_duration)
        if skill.slow_duration > 0 and skill.slow_factor < 1.0:
            primary_enemy.apply_slow(skill.slow_factor, skill.slow_duration)
        if skill.hit_stun > 0:
            primary_enemy.apply_stun(skill.hit_stun)

        if skill.chain_targets > 0 and skill.chain_range > 0:
            self._apply_chain(primary_enemy, enemies, projectile.damage, skill)
        if skill.explosion_radius > 0:
            self._apply_explosion(primary_enemy, enemies, projectile.damage, skill)

    def _apply_chain(
        self,
        primary_enemy: Enemy,
        enemies: list[Enemy],
        base_damage: int,
        skill: SkillDef,
    ) -> None:
        chained = 0
        for enemy in sorted(
            (enemy for enemy in enemies if enemy.is_alive() and enemy is not primary_enemy),
            key=lambda enemy: (enemy.x - primary_enemy.x) ** 2 + (enemy.y - primary_enemy.y) ** 2,
        ):
            distance_sq = (enemy.x - primary_enemy.x) ** 2 + (enemy.y - primary_enemy.y) ** 2
            if distance_sq > skill.chain_range * skill.chain_range:
                continue
            enemy.take_damage(max(1, int(base_damage * max(skill.chain_damage_ratio, 0.5))))
            if skill.hit_stun > 0:
                enemy.apply_stun(skill.hit_stun)
            chained += 1
            if chained >= skill.chain_targets:
                break

    def _apply_explosion(
        self,
        primary_enemy: Enemy,
        enemies: list[Enemy],
        base_damage: int,
        skill: SkillDef,
    ) -> None:
        splash_damage = max(1, int(base_damage * max(skill.explosion_damage_ratio, 0.5)))
        for enemy in enemies:
            if not enemy.is_alive() or enemy is primary_enemy:
                continue
            distance_sq = (enemy.x - primary_enemy.x) ** 2 + (enemy.y - primary_enemy.y) ** 2
            if distance_sq <= skill.explosion_radius * skill.explosion_radius:
                enemy.take_damage(splash_damage)
