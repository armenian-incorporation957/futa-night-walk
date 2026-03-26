from __future__ import annotations

import unittest
from pathlib import Path

import game.scenes.run_scene as run_scene_module
from game.content.enemies_loader import load_enemies
from game.content.skills_loader import load_skills
from game.content.waves_loader import load_waves
from game.core.config import GameConfig
from game.core.input import InputState
from game.scenes.game_over_scene import GameOverScene
from game.scenes.menu_scene import MenuScene
from game.scenes.run_scene import RunScene


DATA_DIR = Path(__file__).resolve().parents[1] / "assets" / "data"


class _DummyApp:
    def __init__(self) -> None:
        self.config = GameConfig(data_dir=DATA_DIR)
        self.input_state = InputState()
        self.enemy_defs = load_enemies(DATA_DIR / "enemies.json")
        self.skill_defs = load_skills(DATA_DIR / "skills.json")
        self.waves = load_waves(DATA_DIR / "waves.json")
        self.resources = None


class SceneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _DummyApp()

    def test_run_scene_imports_pygame_helper(self) -> None:
        self.assertTrue(callable(run_scene_module.require_pygame))

    def test_menu_scene_requests_run(self) -> None:
        scene = MenuScene(self.app)
        scene.start_run()
        self.assertEqual(scene.next_scene_name, "run")

    def test_run_scene_requests_game_over_when_player_dies(self) -> None:
        scene = RunScene(self.app)
        scene.player.hp = 0
        scene.player.alive = False

        scene.update(0.016)

        self.assertEqual(scene.next_scene_name, "game_over")

    def test_game_over_scene_restart_requests_run(self) -> None:
        scene = GameOverScene(self.app, score=12)
        scene.restart()
        self.assertEqual(scene.next_scene_name, "run")
