import json
import os
from typing import Optional, List, Dict
from pathlib import Path
from dataclasses import dataclass


MAX_RANKS_HISTORY = 500


@dataclass
class UserStats:
    uid: str
    max_elo: int
    ranks: List[int]
    latest_game_time: int


class UserStatsStorage:
    def __init__(self, storage_file: str = "data/user_stats.json"):
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self._stats: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self._stats = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._stats = {}
        else:
            self._stats = {}

    def _save(self):
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self._stats, f, ensure_ascii=False, indent=2)

    def get_user_stats(self, uid: str) -> Optional[UserStats]:
        if uid not in self._stats:
            return None

        data = self._stats[uid]
        return UserStats(
            uid=uid,
            max_elo=data.get("max_elo", 0),
            ranks=data.get("ranks", []),
            latest_game_time=data.get("latest_game_time", 0)
        )

    def update_user_stats(
        self,
        uid: str,
        new_ranks: List[int],
        new_max_elo: int,
        latest_game_time: int
    ) -> UserStats:
        if uid not in self._stats:
            self._stats[uid] = {
                "max_elo": 0,
                "ranks": [],
                "latest_game_time": 0
            }

        user_data = self._stats[uid]

        if new_max_elo > user_data.get("max_elo", 0):
            user_data["max_elo"] = new_max_elo

        existing_ranks = user_data.get("ranks", [])
        existing_ranks.extend(new_ranks)

        if len(existing_ranks) > MAX_RANKS_HISTORY:
            existing_ranks = existing_ranks[-MAX_RANKS_HISTORY:]

        user_data["ranks"] = existing_ranks

        if latest_game_time > user_data.get("latest_game_time", 0):
            user_data["latest_game_time"] = latest_game_time

        self._save()

        return UserStats(
            uid=uid,
            max_elo=user_data["max_elo"],
            ranks=user_data["ranks"],
            latest_game_time=user_data["latest_game_time"]
        )


user_stats_storage = UserStatsStorage()
