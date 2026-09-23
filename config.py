import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "ufc_bot.db")))
CARD_CACHE_PATH = Path(os.getenv("CARD_CACHE_PATH", str(BASE_DIR / "data" / "cards")))

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN não foi definido. Crie um arquivo .env com DISCORD_TOKEN=seu_token.")
