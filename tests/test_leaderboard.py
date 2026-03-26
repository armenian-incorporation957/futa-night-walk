from __future__ import annotations

import unittest
from pathlib import Path
import shutil
import uuid

from game.core.leaderboard import LeaderboardStore


SCRATCH_DIR = Path(__file__).resolve().parent / "_scratch"


class LeaderboardTests(unittest.TestCase):
    def _make_store(self) -> LeaderboardStore:
        save_dir = SCRATCH_DIR / f"leaderboard_{uuid.uuid4().hex}"
        save_dir.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(save_dir, ignore_errors=True))
        return LeaderboardStore(save_dir)

    def test_store_creates_file_and_loads_empty_board(self) -> None:
        store = self._make_store()

        self.assertTrue(store.path.exists())
        self.assertEqual(store.load(), [])

    def test_store_sorts_by_stage_then_time_and_keeps_top_five(self) -> None:
        store = self._make_store()

        samples = [
            (2, 45),
            (4, 20),
            (4, 35),
            (3, 99),
            (5, 10),
            (1, 500),
            (5, 8),
        ]
        for stage, seconds in samples:
            store.record(stage, seconds)

        entries = store.load()

        self.assertEqual(len(entries), 5)
        ordered_pairs = [(entry.stage_reached, entry.survival_time_seconds) for entry in entries]
        self.assertEqual(ordered_pairs[0], (5, 10))
        self.assertEqual(ordered_pairs[1], (5, 8))
        self.assertEqual(ordered_pairs[2], (4, 35))
        self.assertEqual(ordered_pairs[3], (4, 20))
