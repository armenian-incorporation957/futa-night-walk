from __future__ import annotations

import unittest
from pathlib import Path

from game.content.skills_loader import load_skills
from game.ui.hud import Hud
from game.ui.skill_views import build_skill_detail_view, build_upgrade_delta_view


DATA_DIR = Path(__file__).resolve().parents[1] / "assets" / "data"


class SkillViewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_defs = load_skills(DATA_DIR / "skills.json")

    def test_skill_detail_view_contains_three_level_snapshots(self) -> None:
        detail = build_skill_detail_view(self.skill_defs["fire_talisman"])

        self.assertEqual(detail.name, "\u706b\u7b26")
        self.assertEqual(set(detail.level_lines), {1, 2, 3})
        self.assertTrue(any("\u707c\u70e7\u4f24\u5bb3" in line for line in detail.level_lines[1]))
        self.assertTrue(any("\u51b7\u5374" in line for line in detail.level_lines[3]))

    def test_upgrade_delta_view_shows_only_changed_fields_after_first_level(self) -> None:
        delta = build_upgrade_delta_view(self.skill_defs["fire_talisman"], current_level=1)

        self.assertEqual(delta.from_level, 1)
        self.assertEqual(delta.to_level, 2)
        self.assertTrue(any("->" in line for line in delta.change_lines))
        self.assertFalse(any("\u51b7\u5374" in line for line in delta.change_lines))

    def test_hud_build_skill_entries_returns_all_unlocked_skills(self) -> None:
        class DummyApp:
            def __init__(self, skill_defs):
                self.skill_defs = skill_defs

        class DummyPlayer:
            def __init__(self):
                self.skill_levels = {
                    "fire_talisman": 1,
                    "thunder_mark": 2,
                    "frost_sand": 1,
                    "spirit_orb": 3,
                    "ward_shard": 2,
                }

        class DummyRunState:
            def __init__(self):
                self.selected_skills = list(DummyPlayer().skill_levels)

        hud = Hud()
        app = DummyApp(self.skill_defs)
        player = DummyPlayer()
        run_state = DummyRunState()

        entries = hud.build_skill_entries(app, player, run_state)

        self.assertEqual(len(entries), 5)
        self.assertEqual(entries[-1].name, self.skill_defs["ward_shard"].name)
