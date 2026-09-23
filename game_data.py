import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TOKEN = os.getenv("DISCORD_TOKEN", "")
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "ufc_bot.db")))
CARD_CACHE_PATH = Path(os.getenv("CARD_CACHE_PATH", str(BASE_DIR / "data" / "cards")))
