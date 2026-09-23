from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from config import CARD_CACHE_PATH
from game_data import PLAYER_LIBRARY

DEFAULT_FONT_PATHS = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"]

def _load_font(size: int):
    for path in DEFAULT_FONT_PATHS:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            pass
    return ImageFont.load_default()

def generate_card(player_id: str, output_dir: Optional[Path] = None) -> Path:
    player = PLAYER_LIBRARY.get(player_id, PLAYER_LIBRARY["ROMARIO"])
    output_dir = output_dir or CARD_CACHE_PATH
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{player_id.lower()}.png"
    image = Image.new("RGB", (720, 1040), (28, 20, 20) if player.get("is_dragon") else (18, 18, 22))
    draw = ImageDraw.Draw(image)
    color = (255, 215, 0) if player.get("is_dragon") else (222, 18, 40)
    draw.rounded_rectangle((30, 30, 690, 1010), radius=32, fill=(10, 10, 14), outline=color, width=6)
    draw.text((360, 100), "UFC DRAGON" if player.get("is_dragon") else "UFC FIGHTER", fill=color, anchor="mm", font=_load_font(30))
    draw.text((360, 190), str(player["ovr"]), fill="white", anchor="mm", font=_load_font(84))
    draw.text((360, 290), player["name"].upper(), fill="white", anchor="mm", font=_load_font(40))
    stats = [("ATAQUE", player["attack"]), ("DEFESA", player["defense"]), ("FÍSICO", player["physical"]), ("ENERGIA", player["energy"])]
    for i, (name, value) in enumerate(stats):
        x, y = 140 + (i % 2) * 240, 450 + (i // 2) * 160
        draw.rounded_rectangle((x, y, x + 180, y + 110), radius=18, fill=(40, 40, 48), outline=color)
        draw.text((x + 90, y + 30), name, fill=(200, 200, 210), anchor="mm", font=_load_font(17))
        draw.text((x + 90, y + 75), str(value), fill="white", anchor="mm", font=_load_font(36))
    draw.text((360, 900), f"OVR {player['ovr']}", fill="white", anchor="mm", font=_load_font(30))
    image.save(path)
    return path
