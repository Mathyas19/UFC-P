import random
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

from config import DATABASE_PATH
from game_data import DRAGON_DROP_RATE, EXCLUSIVE_PLAYERS, NORMAL_PLAYERS, STARTER_PLAYERS, get_player_by_id


class DatabaseManager:
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def ensure_schema(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    level INTEGER DEFAULT 0,
                    ufc_points INTEGER DEFAULT 0,
                    energy INTEGER DEFAULT 50,
                    wins INTEGER DEFAULT 0,
                    draws INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    matches_played INTEGER DEFAULT 0,
                    dragon_boxes INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_players (
                    user_id TEXT,
                    player_id TEXT,
                    is_dragon INTEGER DEFAULT 0,
                    quantity INTEGER DEFAULT 1,
                    obtained_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, player_id)
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS match_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    opponent_id TEXT,
                    result TEXT,
                    fighter TEXT,
                    opponent_fighter TEXT,
                    summary TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def get_or_create_user(self, user_id: str, username: str) -> Dict:
        with self._connect() as conn:
            profile = conn.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()

            if profile is None:
                conn.execute(
                    "INSERT INTO users (user_id, username, level, ufc_points, energy) VALUES (?, ?, 0, 0, 50)",
                    (user_id, username),
                )
                for player_id in STARTER_PLAYERS:
                    conn.execute(
                        "INSERT OR IGNORE INTO user_players (user_id, player_id, is_dragon, quantity) VALUES (?, ?, 0, 1)",
                        (user_id, player_id),
                    )
                profile = conn.execute(
                    "SELECT * FROM users WHERE user_id = ?",
                    (user_id,),
                ).fetchone()

        return self.get_user_profile(user_id)

    def get_user_profile(self, user_id: str) -> Dict:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
            if row is None:
                return {
                    "user_id": user_id,
                    "username": "Desconhecido",
                    "level": 0,
                    "ufc_points": 0,
                    "energy": 50,
                    "wins": 0,
                    "draws": 0,
                    "losses": 0,
                    "matches_played": 0,
                    "dragon_boxes": 0,
                    "player_count": 0,
                }

            player_count = conn.execute(
                "SELECT COUNT(*) FROM user_players WHERE user_id = ?",
                (user_id,),
            ).fetchone()[0]

            level = max(0, min(100, row["ufc_points"]))
            return {
                "user_id": row["user_id"],
                "username": row["username"],
                "level": level,
                "ufc_points": row["ufc_points"],
                "energy": row["energy"],
                "wins": row["wins"],
                "draws": row["draws"],
                "losses": row["losses"],
                "matches_played": row["matches_played"],
                "dragon_boxes": row["dragon_boxes"],
                "player_count": player_count,
            }

    def get_user_players(self, user_id: str) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT player_id, is_dragon, quantity FROM user_players WHERE user_id = ? ORDER BY player_id ASC",
                (user_id,),
            ).fetchall()

        players = []
        for row in rows:
            player = get_player_by_id(row["player_id"])
            players.append(
                {
                    "player_id": row["player_id"],
                    "name": player["name"],
                    "ovr": player["ovr"],
                    "position": player["position"],
                    "is_dragon": bool(row["is_dragon"]),
                    "quantity": row["quantity"],
                    "attack": player["attack"],
                    "defense": player["defense"],
                    "physical": player["physical"],
                    "energy": player["energy"],
                }
            )
        return players

    def add_player_to_inventory(self, user_id: str, player_id: str, is_dragon: bool = False) -> Dict:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO user_players (user_id, player_id, is_dragon, quantity)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(user_id, player_id)
                DO UPDATE SET quantity = quantity + 1
                """,
                (user_id, player_id, int(is_dragon)),
            )

        return self.get_user_players(user_id)

    def record_match_result(self, user_id: str, opponent_id: str, result: str, fighter: str, opponent_fighter: str, summary: str):
        result = result.lower()
        with self._connect() as conn:
            if result == "win":
                conn.execute("UPDATE users SET wins = wins + 1, ufc_points = ufc_points + 2, matches_played = matches_played + 1 WHERE user_id = ?", (user_id,))
                conn.execute("UPDATE users SET losses = losses + 1, ufc_points = ufc_points - 2, matches_played = matches_played + 1 WHERE user_id = ?", (opponent_id,))
            elif result == "draw":
                conn.execute("UPDATE users SET draws = draws + 1, matches_played = matches_played + 1 WHERE user_id = ?", (user_id,))
                conn.execute("UPDATE users SET draws = draws + 1, matches_played = matches_played + 1 WHERE user_id = ?", (opponent_id,))
            else:
                conn.execute("UPDATE users SET losses = losses + 1, ufc_points = ufc_points - 2, matches_played = matches_played + 1 WHERE user_id = ?", (user_id,))
                conn.execute("UPDATE users SET wins = wins + 1, ufc_points = ufc_points + 2, matches_played = matches_played + 1 WHERE user_id = ?", (opponent_id,))

            conn.execute(
                "INSERT INTO match_history (user_id, opponent_id, result, fighter, opponent_fighter, summary) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, opponent_id, result, fighter, opponent_fighter, summary),
            )

        self.award_dragon_box_if_needed(user_id)
        self.award_dragon_box_if_needed(opponent_id)

    def award_dragon_box_if_needed(self, user_id: str):
        profile = self.get_user_profile(user_id)
        if profile["matches_played"] > 0 and profile["matches_played"] % 50 == 0:
            with self._connect() as conn:
                conn.execute("UPDATE users SET dragon_boxes = dragon_boxes + 1 WHERE user_id = ?", (user_id,))

    def use_energy(self, user_id: str, amount: int = 1):
        with self._connect() as conn:
            conn.execute("UPDATE users SET energy = MAX(0, energy - ?) WHERE user_id = ?", (amount, user_id))

    def recover_energy(self, user_id: str, amount: int = 1):
        with self._connect() as conn:
            conn.execute("UPDATE users SET energy = MIN(50, energy + ?) WHERE user_id = ?", (amount, user_id))

    def open_dragon_chest(self, user_id: str) -> Dict:
        profile = self.get_user_profile(user_id)
        if profile["dragon_boxes"] <= 0:
            return {"opened": False, "reason": "Você não possui nenhuma Caixa UFC Dragon.", "reward": None, "is_dragon": False}

        with self._connect() as conn:
            conn.execute("UPDATE users SET dragon_boxes = dragon_boxes - 1 WHERE user_id = ?", (user_id,))

        chance = random.random()
        if chance <= DRAGON_DROP_RATE:
            reward = random.choice(EXCLUSIVE_PLAYERS)["id"]
            self.add_player_to_inventory(user_id, reward, is_dragon=True)
            return {"opened": True, "reason": "Você abriu uma Caixa UFC Dragon e encontrou um jogador exclusivo!", "reward": reward, "is_dragon": True}

        reward = random.choice(NORMAL_PLAYERS)["id"]
        self.add_player_to_inventory(user_id, reward, is_dragon=False)
        return {"opened": True, "reason": "Você abriu uma Caixa UFC Dragon, mas não conseguiu um dragão.", "reward": reward, "is_dragon": False}

    def get_total_history(self, user_id: str) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM match_history WHERE user_id = ? ORDER BY id DESC LIMIT 10",
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_fighter_for_user(self, user_id: str) -> str:
        players = self.get_user_players(user_id)
        if not players:
            return "ROMARIO"
        return max(players, key=lambda item: item["ovr"])["player_id"]
