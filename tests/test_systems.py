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
            [WaveDef(time=1.0, enemy_id="paper_spirit", count=3, interval=0.5)],
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
            [WaveDef(time=0.5, enemy_id="paper_spirit", count=1, interval=0.0)],
            rng=random.Random(2),
        )

        spawn_system.set_active_enemy_count(0)
        endless = spawn_system.update(8.0, self.enemy_defs, (0, 0, 100, 100))

        self.assertGreaterEqual(len(endless), 1)

    def test_spawn_system_respects_soft_cap_in_endless_mode(self) -> None:
        spawn_system = SpawnSystem([], rng=random.Random(3))
        spawn_system.set_active_enemy_count(999)

        endless = spawn_system.update(12.0, self.enemy_defs, (0, 0, 100, 100))

        self.assertEqual(len(endless), 0)

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
        player.skill_timers["ward_shard"] = 0.0
        combat = CombatSystem()

        spawned = combat.spawn_player_projectiles(player, [], self.skill_defs, [])

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

    def test_progression_choices_are_unique_and_valid(self) -> None:
        player = Player(0, 0, PlayerStats())
        progression = ProgressionSystem(self.skill_defs, rng=random.Random(2))
        progression.apply_upgrade(player, "fire_talisman")

        choices = progression.build_upgrade_choices(player, count=3)

        self.assertEqual(len(choices), len(set(choices)))
        for choice in choices:
            self.assertIn(choice, self.skill_defs)
            self.assertNotIn(choice, ["fire_talisman"])

    def test_player_levels_after_collecting_enough_exp(self) -> None:
        player = Player(0, 0, PlayerStats())
        progression = ProgressionSystem(self.skill_defs)

        leveled_up = progression.grant_exp(player, 25)

        self.assertTrue(leveled_up)
        self.assertEqual(player.level, 2)
        self.assertEqual(player.exp, 5)
