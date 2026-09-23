import random
from typing import Dict

NORMAL_PLAYERS = [
    {"id": "ROMARIO", "name": "Romário", "ovr": 85, "attack": 88, "defense": 64, "physical": 80, "energy": 85, "position": "ATA", "rarity": "normal", "is_dragon": False},
    {"id": "LUIS_FABIANO", "name": "Luis Fabiano", "ovr": 85, "attack": 86, "defense": 62, "physical": 82, "energy": 83, "position": "ATA", "rarity": "normal", "is_dragon": False},
    {"id": "FELIPE_MELO", "name": "Felipe Melo", "ovr": 85, "attack": 71, "defense": 86, "physical": 86, "energy": 80, "position": "VOL", "rarity": "normal", "is_dragon": False},
    {"id": "DIEGO_COSTA", "name": "Diego Costa", "ovr": 85, "attack": 84, "defense": 66, "physical": 87, "energy": 82, "position": "ATA", "rarity": "normal", "is_dragon": False},
    {"id": "GATTUSO", "name": "Gattuso", "ovr": 85, "attack": 72, "defense": 82, "physical": 88, "energy": 84, "position": "VOL", "rarity": "normal", "is_dragon": False},
]
EXCLUSIVE_PLAYERS = [
    {"id": "PEPE", "name": "Pepe", "ovr": 100, "attack": 96, "defense": 94, "physical": 97, "energy": 95, "position": "ZAG", "rarity": "exclusive", "is_dragon": True},
    {"id": "SERGIO_RAMOS", "name": "Sergio Ramos", "ovr": 100, "attack": 92, "defense": 95, "physical": 98, "energy": 93, "position": "ZAG", "rarity": "exclusive", "is_dragon": True},
]
PLAYER_LIBRARY = {p["id"]: p for p in NORMAL_PLAYERS + EXCLUSIVE_PLAYERS}
STYLES = {"Ataque": {"offense_bonus": 1.18, "defense_bonus": .92}, "Defesa": {"offense_bonus": .92, "defense_bonus": 1.2}, "Contra-ataque": {"offense_bonus": 1.05, "defense_bonus": 1.08}, "Equilibrado": {"offense_bonus": 1, "defense_bonus": 1}, "Pressão": {"offense_bonus": 1.12, "defense_bonus": .96}, "Paciência": {"offense_bonus": .98, "defense_bonus": 1.06}}
STARTER_PLAYERS = ["ROMARIO", "LUIS_FABIANO", "FELIPE_MELO"]
DRAGON_DROP_RATE = 0.000000001

def get_player_by_id(player_id: str) -> Dict:
    return PLAYER_LIBRARY.get(player_id, PLAYER_LIBRARY["ROMARIO"]).copy()
