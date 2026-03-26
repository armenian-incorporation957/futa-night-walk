from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, UTC
from pathlib import Path


@dataclass(frozen=True)
class LeaderboardEntry:
    stage_reached: int
    survival_time_seconds: int
    created_at: str


class LeaderboardStore:
    def __init__(self, save_dir: Path) -> None:
        self.save_dir = Path(save_dir)
        self.path = self.save_dir / "endless_leaderboard.json"
        self.save_dir.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def load(self) -> list[LeaderboardEntry]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            return []
        entries: list[LeaderboardEntry] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            try:
                entries.append(
                    LeaderboardEntry(
                        stage_reached=int(item["stage_reached"]),
                        survival_time_seconds=int(item["survival_time_seconds"]),
                        created_at=str(item["created_at"]),
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue
        return self._sorted(entries)

    def record(self, stage_reached: int, survival_time_seconds: int) -> list[LeaderboardEntry]:
        entries = self.load()
        entries.append(
            LeaderboardEntry(
                stage_reached=stage_reached,
                survival_time_seconds=survival_time_seconds,
                created_at=datetime.now(UTC).isoformat(),
            )
        )
        entries = self._sorted(entries)[:5]
        self.path.write_text(
            json.dumps([asdict(entry) for entry in entries], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return entries

    def _sorted(self, entries: list[LeaderboardEntry]) -> list[LeaderboardEntry]:
        return sorted(
            entries,
            key=lambda entry: (entry.stage_reached, entry.survival_time_seconds, entry.created_at),
            reverse=True,
        )
