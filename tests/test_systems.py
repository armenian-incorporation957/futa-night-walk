from __future__ import annotations

import random
import unittest
from pathlib import Path

from game.content.enemies_loader import load_enemies
from game.content.skills_loader import load_skills
from game.content.waves_loader import load_waves
from game.entities.enemy import Enemy
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

    def test_spawn_system_respects_wave_schedule(self) -> None:
        spawn_system = SpawnSystem(
            [WaveDef(time=1.0, enemy_id="paper_spirit", count=3, interval=0.5)],
            rng=random.Random(1),
        )

        none_spawned = spawn_system.update(0.9, self.enemy_defs, (0, 0, 100, 100))
        first_batch = spawn_system.update(1.0, self.enemy_defs, (0, 0, 100, 100))
        second_batch = spawn_system.update(2.0, self.enemy_defs, (0, 0, 100, 100))

        self.assertEqual(len(none_spawned), 0)
        self.assertEqual(len(first_batch), 1)
        self.assertEqual(len(second_batch), 2)

    def test_combat_system_applies_damage_and_collects_exp(self) -> None:
        player = Player(50, 50, PlayerStats())
        enemy = Enemy(self.enemy_defs["paper_spirit"], 90, 50)
        projectile = Projectile(
            x=90,
            y=50,
            direction=(1, 0),
            speed=0,
            damage=20,
            lifetime=1.0,
            color=(255, 255, 255),
            owner_skill="fire_talisman",
            owner_faction="player",
        )

        combat = CombatSystem()
        pickups = []
        exp = combat.resolve([projectile], [enemy], pickups, player)

        self.assertEqual(exp, 0)
        self.assertFalse(enemy.is_alive())
        self.assertEqual(len(pickups), 1)

        pickups[0].x = player.x
        pickups[0].y = player.y
        exp = combat.resolve([], [], pickups, player)
        self.assertGreater(exp, 0)

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
