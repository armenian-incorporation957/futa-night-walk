from __future__ import annotations

import random
import unittest
from pathlib import Path

from game.content.enemies_loader import load_enemies
from game.content.skills_loader import load_skills
from game.entities.enemy import Enemy
from game.entities.pickup import Pickup
from game.entities.player import Player
from game.entities.projectile import Projectile
from game.models.definitions import PlayerStats, WaveDef
from game.systems.combat_system import CombatSystem
from game.systems.progression_system import ProgressionSystem
from game.systems.spawn_system import SpawnSystem


DATA_DIR = Path(__file__).resolve().parents[1] / "assets" / "data"


class SystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.enemy_defs = load_enemies(DATA_DIR / "enemies.json")
        self.skill_defs = load_skills(DATA_DIR / "skills.json")

    def _projectile(self, skill_id: str, x: float, y: float) -> Projectile:
        return Projectile(
            x=x,
            y=y,
            direction=(1, 0),
            speed=0,
            skill=self.skill_defs[skill_id],
            lifetime=1.0,
            color=(255, 255, 255),
            owner_faction="player",
        )

    def test_spawn_system_respects_wave_schedule(self) -> None:
        spawn_system = SpawnSystem(
            [WaveDef(stage=1, time=1.0, enemy_id="paper_spirit", count=3, interval=0.5)],
            rng=random.Random(1),
        )

        none_spawned = spawn_system.update(0.9, self.enemy_defs, (0, 0, 100, 100))
        first_batch = spawn_system.update(1.0, self.enemy_defs, (0, 0, 100, 100))
        spawn_system.set_active_enemy_count(999)
        second_batch = spawn_system.update(2.0, self.enemy_defs, (0, 0, 100, 100))

        self.assertEqual(len(none_spawned), 0)
        self.assertEqual(len(first_batch), 1)
        self.assertEqual(len(second_batch), 2)

    def test_spawn_system_continues_after_scripted_waves(self) -> None:
        spawn_system = SpawnSystem(
            [WaveDef(stage=1, time=0.5, enemy_id="paper_spirit", count=1, interval=0.0)],
            rng=random.Random(2),
        )

        spawn_system.set_active_enemy_count(0)
        endless = spawn_system.update(8.0, self.enemy_defs, (0, 0, 100, 100))

        self.assertGreaterEqual(len(endless), 1)

    def test_spawn_system_respects_soft_cap_in_director_mode(self) -> None:
        spawn_system = SpawnSystem([], rng=random.Random(3))
        spawn_system.configure_stage(stage_pattern=4, difficulty_multiplier=1.0)
        spawn_system.set_active_enemy_count(999)

        endless = spawn_system.update(12.0, self.enemy_defs, (0, 0, 100, 100))

        self.assertEqual(len(endless), 0)

    def test_spawn_system_scales_enemy_stats_in_later_cycles(self) -> None:
        spawn_system = SpawnSystem([], rng=random.Random(4))
        spawn_system.configure_stage(stage_pattern=3, difficulty_multiplier=1.12)
        spawn_system.set_active_enemy_count(0)

        spawned = spawn_system.update(10.0, self.enemy_defs, (0, 0, 100, 100))

        self.assertTrue(spawned)
        enemy = spawned[0]
        self.assertGreaterEqual(enemy.max_hp, self.enemy_defs[enemy.definition.id].hp)
        self.assertGreaterEqual(enemy.contact_damage, self.enemy_defs[enemy.definition.id].contact_damage)

    def test_fire_talisman_applies_burn(self) -> None:
        player = Player(50, 50, PlayerStats())
        enemy = Enemy(self.enemy_defs["lantern_wisp"], 90, 50)
        projectile = self._projectile("fire_talisman", 90, 50)

        combat = CombatSystem()
        combat.resolve([projectile], [enemy], [], player)

        self.assertGreater(enemy.burn_timer, 0.0)
        self.assertGreater(enemy.burn_damage, 0.0)

    def test_thunder_mark_chains_to_second_enemy(self) -> None:
        player = Player(50, 50, PlayerStats())
        first_enemy = Enemy(self.enemy_defs["lantern_wisp"], 90, 50)
        second_enemy = Enemy(self.enemy_defs["paper_spirit"], 120, 50)
        projectile = self._projectile("thunder_mark", 90, 50)

        combat = CombatSystem()
        combat.resolve([projectile], [first_enemy, second_enemy], [], player)

        self.assertLess(second_enemy.hp, second_enemy.max_hp)

    def test_frost_sand_applies_slow(self) -> None:
        player = Player(50, 50, PlayerStats())
        enemy = Enemy(self.enemy_defs["mist_fox"], 90, 50)
        projectile = self._projectile("frost_sand", 90, 50)

        combat = CombatSystem()
        combat.resolve([projectile], [enemy], [], player)

        self.assertGreater(enemy.slow_timer, 0.0)
        self.assertLess(enemy.slow_factor, 1.0)

    def test_spirit_orb_explodes_on_nearby_enemies(self) -> None:
        player = Player(50, 50, PlayerStats())
        first_enemy = Enemy(self.enemy_defs["lantern_wisp"], 90, 50)
        second_enemy = Enemy(self.enemy_defs["paper_spirit"], 110, 55)
        projectile = self._projectile("spirit_orb", 90, 50)

        combat = CombatSystem()
        combat.resolve([projectile], [first_enemy, second_enemy], [], player)

        self.assertLess(second_enemy.hp, second_enemy.max_hp)

    def test_ward_shard_spawns_orbit_projectiles(self) -> None:
        player = Player(0, 0, PlayerStats())
        player.owned_skills.append("ward_shard")
        player.skill_levels["ward_shard"] = 1
        player.skill_timers["ward_shard"] = 0.0
        combat = CombatSystem()

        spawned = combat.spawn_player_projectiles(player, [], {"ward_shard": self.skill_defs["ward_shard"]}, [])

        self.assertEqual(len(spawned), self.skill_defs["ward_shard"].orbit_count)
        self.assertTrue(all(projectile.skill.behavior_type == "orbit_guard" for projectile in spawned))

    def test_pickups_are_attracted_and_auto_collected(self) -> None:
        player = Player(50, 50, PlayerStats())
        pickup = Pickup(120, 50, 7)
        combat = CombatSystem()

        gained_exp = combat.update_pickups([pickup], player, 0.2)
        self.assertEqual(gained_exp, 0)
        self.assertTrue(pickup.attracted)
        self.assertLess(pickup.x, 120)

        pickup.x = 60
        pickup.y = 50
        gained_exp = combat.update_pickups([pickup], player, 0.1)
        self.assertGreater(gained_exp, 0)
        self.assertFalse(pickup.is_alive())

    def test_normal_projectile_is_not_removed_only_by_time_before_leaving_bounds(self) -> None:
        projectile = Projectile(
            x=50,
            y=50,
            direction=(1, 0),
            speed=0,
            skill=self.skill_defs["fire_talisman"],
            lifetime=0.05,
            color=(255, 255, 255),
            owner_faction="player",
            uses_lifetime=False,
        )
        combat = CombatSystem()

        combat.update_projectiles([projectile], 1.0, (0, 0, 100, 100), Player(0, 0, PlayerStats()), [])

        self.assertTrue(projectile.is_alive())

    def test_orbit_projectile_still_expires_by_lifetime(self) -> None:
        projectile = Projectile(
            x=50,
            y=50,
            direction=(1, 0),
            speed=0,
            skill=self.skill_defs["ward_shard"],
            lifetime=0.05,
            color=(255, 255, 255),
            owner_faction="player",
            uses_lifetime=True,
        )
        combat = CombatSystem()

        combat.update_projectiles([projectile], 0.1, (0, 0, 100, 100), Player(0, 0, PlayerStats()), [])

        self.assertFalse(projectile.is_alive())

    def test_progression_cycle_pools_cover_all_twenty_skills_without_duplicates(self) -> None:
        progression = ProgressionSystem(self.skill_defs, rng=random.Random(5))

        pools = progression.build_cycle_stage_pools(1)
        flattened = [skill_id for pool in pools for skill_id in pool]

        self.assertEqual(len(pools), 4)
        self.assertEqual(len(flattened), 20)
        self.assertEqual(len(set(flattened)), 20)
        self.assertTrue(all(len(pool) == 5 for pool in pools))

    def test_progression_choices_only_offer_unmaxed_stage_skills(self) -> None:
        progression = ProgressionSystem(self.skill_defs, rng=random.Random(6))
        stage_skill_pool = progression.get_stage_skill_pool(1)
        stage_skill_levels = {skill_id: 0 for skill_id in stage_skill_pool}
        stage_skill_levels[stage_skill_pool[0]] = 3

        choices = progression.build_upgrade_choices(stage_skill_pool, stage_skill_levels, count=3)

        self.assertEqual(len(choices), len(set(choices)))
        self.assertNotIn(stage_skill_pool[0], choices)
        self.assertTrue(all(choice in stage_skill_pool for choice in choices))

    def test_apply_upgrade_unlocks_skill_and_caps_at_three(self) -> None:
        player = Player(0, 0, PlayerStats())
        progression = ProgressionSystem(self.skill_defs)
        stage_skill_levels = {"fire_talisman": 0}

        first_level = progression.apply_upgrade(player, "fire_talisman", stage_skill_levels)
        second_level = progression.apply_upgrade(player, "fire_talisman", stage_skill_levels)
        third_level = progression.apply_upgrade(player, "fire_talisman", stage_skill_levels)

        self.assertEqual((first_level, second_level, third_level), (1, 2, 3))
        self.assertIn("fire_talisman", player.owned_skills)
        self.assertEqual(player.skill_levels["fire_talisman"], 3)
        with self.assertRaises(ValueError):
            progression.apply_upgrade(player, "fire_talisman", stage_skill_levels)

    def test_effective_skill_defs_apply_level_scaling(self) -> None:
        progression = ProgressionSystem(self.skill_defs)

        effective = progression.effective_skill_defs({"fire_talisman": 3})

        self.assertEqual(effective["fire_talisman"].damage, 14)
        self.assertEqual(effective["fire_talisman"].cooldown, 0.34)
        self.assertEqual(effective["fire_talisman"].burn_duration, 2.4)

    def test_all_stage_skills_maxed_requires_every_skill_at_three(self) -> None:
        progression = ProgressionSystem(self.skill_defs)
        pool = progression.get_stage_skill_pool(1)
        levels = {skill_id: 3 for skill_id in pool}

        self.assertTrue(progression.all_stage_skills_maxed(pool, levels))
        levels[pool[0]] = 2
        self.assertFalse(progression.all_stage_skills_maxed(pool, levels))

    def test_player_levels_after_collecting_enough_exp(self) -> None:
        player = Player(0, 0, PlayerStats())
        progression = ProgressionSystem(self.skill_defs)

        leveled_up = progression.grant_exp(player, 25)

        self.assertTrue(leveled_up)
        self.assertEqual(player.level, 2)
        self.assertEqual(player.exp, 5)
