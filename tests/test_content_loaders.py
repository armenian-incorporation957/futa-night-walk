from __future__ import annotations

import json
import unittest
import uuid
from pathlib import Path

from game.content.enemies_loader import load_enemies
from game.content.skills_loader import load_skills
from game.content.waves_loader import load_waves


DATA_DIR = Path(__file__).resolve().parents[1] / "assets" / "data"
SCRATCH_DIR = Path(__file__).resolve().parent / "_scratch"


class ContentLoaderTests(unittest.TestCase):
    def _write_payload(self, filename: str, payload: list[dict[str, object]]) -> Path:
        path = SCRATCH_DIR / f"{uuid.uuid4().hex}_{filename}"
        path.write_text(json.dumps(payload), encoding="utf-8")
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        return path

    def test_default_data_loads(self) -> None:
        enemies = load_enemies(DATA_DIR / "enemies.json")
        skills = load_skills(DATA_DIR / "skills.json")
        waves = load_waves(DATA_DIR / "waves.json")

        self.assertIn("paper_spirit", enemies)
        self.assertIn("fire_talisman", skills)
        self.assertEqual(len(skills), 20)
        self.assertGreaterEqual(len(waves), 8)
        self.assertEqual(enemies["paper_spirit"].name, "\u7eb8\u7075")
        self.assertEqual(skills["fire_talisman"].name, "\u706b\u7b26")
        self.assertEqual(skills["fire_talisman"].level_scaling[3]["cooldown"], 0.34)
        self.assertTrue(all(wave.stage > 0 for wave in waves))

    def test_enemy_loader_rejects_duplicates(self) -> None:
        payload = [
            {
                "id": "dup",
                "name": "A",
                "hp": 10,
                "speed": 1,
                "contact_damage": 1,
                "sprite_key": "s",
                "ai_type": "chase",
            },
            {
                "id": "dup",
                "name": "B",
                "hp": 10,
                "speed": 1,
                "contact_damage": 1,
                "sprite_key": "s",
                "ai_type": "chase",
            },
        ]
        path = self._write_payload("enemies.json", payload)
        with self.assertRaises(ValueError):
            load_enemies(path)

    def test_skill_loader_rejects_missing_fields(self) -> None:
        payload = [{"id": "bad", "name": "missing"}]
        path = self._write_payload("skills.json", payload)
        with self.assertRaises(ValueError):
            load_skills(path)

    def test_waves_loader_rejects_bad_counts(self) -> None:
        payload = [{"stage": 1, "time": 0, "enemy_id": "paper_spirit", "count": 0, "interval": 1}]
        path = self._write_payload("waves.json", payload)
        with self.assertRaises(ValueError):
            load_waves(path)
