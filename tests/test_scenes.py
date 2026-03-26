from __future__ import annotations

import unittest
from pathlib import Path

import game.scenes.run_scene as run_scene_module
from game.content.enemies_loader import load_enemies
from game.content.skills_loader import load_skills
from game.content.waves_loader import load_waves
from game.core.config import GameConfig
from game.core.input import InputState
from game.core.pygame_support import require_pygame
from game.scenes.game_over_scene import GameOverScene
from game.scenes.menu_scene import MenuScene
from game.scenes.run_scene import RunScene


DATA_DIR = Path(__file__).resolve().parents[1] / "assets" / "data"


class _DummyLeaderboard:
    def __init__(self) -> None:
        self.entries: list[tuple[int, int]] = []

    def load(self) -> list[object]:
        return []

    def record(self, stage_reached: int, survival_time_seconds: int) -> None:
        self.entries.append((stage_reached, survival_time_seconds))


class _DummyApp:
    def __init__(self) -> None:
        self.config = GameConfig(data_dir=DATA_DIR)
        self.input_state = InputState()
        self.enemy_defs = load_enemies(DATA_DIR / "enemies.json")
        self.skill_defs = load_skills(DATA_DIR / "skills.json")
        self.waves = load_waves(DATA_DIR / "waves.json")
        self.resources = None
        self.leaderboard = _DummyLeaderboard()


class SceneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _DummyApp()
        self.pygame = require_pygame()

    def _click(self, scene: MenuScene, position: tuple[int, int]) -> None:
        scene.handle_event(self.pygame.event.Event(self.pygame.MOUSEMOTION, {"pos": position}))
        scene.handle_event(self.pygame.event.Event(self.pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": position}))
        scene.handle_event(self.pygame.event.Event(self.pygame.MOUSEBUTTONUP, {"button": 1, "pos": position}))

    def test_run_scene_imports_pygame_helper(self) -> None:
        self.assertTrue(callable(run_scene_module.require_pygame))

    def test_menu_scene_click_campaign_requests_run(self) -> None:
        scene = MenuScene(self.app)
        rect = scene._button_rect(-50)

        self._click(scene, rect.center)

        self.assertEqual(scene.next_scene_name, "run")
        self.assertEqual(scene.next_scene_kwargs["game_mode"], "campaign")

    def test_menu_scene_click_endless_requests_run(self) -> None:
        scene = MenuScene(self.app)
        rect = scene._button_rect(20)

        self._click(scene, rect.center)

        self.assertEqual(scene.next_scene_name, "run")
        self.assertEqual(scene.next_scene_kwargs["game_mode"], "endless")

    def test_menu_scene_help_toggles_popup(self) -> None:
        scene = MenuScene(self.app)
        rect = scene._button_rect(90)

        self._click(scene, rect.center)
        self.assertTrue(scene.show_help)
        self._click(scene, rect.center)
        self.assertFalse(scene.show_help)

    def test_menu_scene_help_tab_switches_to_skills(self) -> None:
        scene = MenuScene(self.app)
        scene.show_help = True
        rect = scene._help_tab_rect("skills")

        self._click(scene, rect.center)

        self.assertEqual(scene.help_tab, "skills")

    def test_menu_scene_enter_no_longer_starts_game(self) -> None:
        scene = MenuScene(self.app)
        event = self.pygame.event.Event(self.pygame.KEYDOWN, {"key": self.pygame.K_RETURN})

        scene.handle_event(event)

        self.assertIsNone(scene.next_scene_name)

    def test_menu_scene_hover_state_updates_on_motion(self) -> None:
        scene = MenuScene(self.app)
        rect = scene._button_rect(90)
        scene.handle_event(self.pygame.event.Event(self.pygame.MOUSEMOTION, {"pos": rect.center}))
        self.assertEqual(scene.hovered_button, "help")

    def test_run_scene_intro_transitions_to_starter_select(self) -> None:
        scene = RunScene(self.app, game_mode="campaign")

        scene.update(1.0)

        self.assertEqual(scene.run_state.stage_state, "starter_select")
        self.assertEqual(scene.run_state.pending_upgrade_choices, scene.run_state.stage_skill_pool)
        self.assertEqual(len(scene.run_state.stage_skill_pool), 5)

    def test_run_scene_maxing_last_skill_starts_transition_and_next_stage(self) -> None:
        scene = RunScene(self.app, game_mode="campaign")
        scene.player.hp = 40
        scene.update(1.0)
        final_skill = scene.run_state.stage_skill_pool[0]
        scene.run_state.stage_skill_levels = {skill_id: 3 for skill_id in scene.run_state.stage_skill_pool}
        scene.run_state.stage_skill_levels[final_skill] = 2
        scene.run_state.pending_upgrade_choices = [final_skill]
        scene.run_state.stage_state = "upgrade"

        scene._resolve_upgrade_selection(0)

        self.assertEqual(scene.run_state.stage_state, "transition")
        scene.update(1.0)
        self.assertEqual(scene.run_state.stage_index, 2)
        self.assertEqual(scene.player.hp, 60)
        self.assertEqual(scene.player.level, 1)
        self.assertEqual(scene.run_state.stage_state, "intro")

    def test_run_scene_campaign_completion_requests_victory_scene(self) -> None:
        scene = RunScene(self.app, game_mode="campaign")
        scene.start_stage(4, heal_amount=0)
        scene.complete_stage()

        scene.update(1.0)

        self.assertEqual(scene.next_scene_name, "game_over")
        self.assertTrue(scene.next_scene_kwargs["victory"])
        self.assertEqual(scene.next_scene_kwargs["stage_reached"], 4)

    def test_run_scene_requests_game_over_and_records_endless_result_when_player_dies(self) -> None:
        scene = RunScene(self.app, game_mode="endless")
        scene.run_state.current_time = 37.0
        scene.player.hp = 0
        scene.player.alive = False

        scene.update(0.016)

        self.assertEqual(scene.next_scene_name, "game_over")
        self.assertEqual(scene.next_scene_kwargs["game_mode"], "endless")
        self.assertEqual(self.app.leaderboard.entries, [(1, 37)])

    def test_game_over_scene_restart_requests_run_with_same_mode(self) -> None:
        scene = GameOverScene(self.app, score=12, stage_reached=3, game_mode="endless")

        scene.restart()

        self.assertEqual(scene.next_scene_name, "run")
        self.assertEqual(scene.next_scene_kwargs["game_mode"], "endless")
