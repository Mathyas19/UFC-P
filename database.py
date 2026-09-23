from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from config import CARD_CACHE_PATH
from game_data import PLAYER_LIBRARY


DEFAULT_FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def _load_font(size: int, bold: bool = True):
    for font_path in DEFAULT_FONT_PATHS:
        try:
            return ImageFont.truetype(font_path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def _rounded_box(draw, xy, radius=30, fill=(255, 255, 255, 240), outline=None, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def generate_card(player_id: str, output_dir: Optional[Path] = None) -> Path:
    player = PLAYER_LIBRARY.get(player_id, PLAYER_LIBRARY["ROMARIO"]).copy()
    is_dragon = bool(player.get("is_dragon"))

    output_dir = output_dir or CARD_CACHE_PATH
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{player_id.lower()}.png"

    width, height = 720, 1040
    image = Image.new("RGBA", (width, height), (18, 18, 22, 255))
    draw = ImageDraw.Draw(image)

    if is_dragon:
        bg_gradient = Image.new("RGBA", (width, height), (24, 18, 12, 255))
        draw_bg = ImageDraw.Draw(bg_gradient)
        for y in range(height):
            ratio = y / height
            r = int(40 + ratio * 130)
            g = int(30 + ratio * 110)
            b = int(18 + ratio * 45)
            draw_bg.line((0, y, width, y), fill=(r, g, b, 255))
        image = bg_gradient
        draw = ImageDraw.Draw(image)
        border_color = (255, 215, 0, 255)
        accent_color = (255, 200, 70, 255)
    else:
        border_color = (222, 18, 40, 255)
        accent_color = (120, 120, 130, 255)

    _rounded_box(draw, (30, 30, width - 30, height - 30), radius=32, fill=(10, 10, 14, 245), outline=border_color, width=6)
    _rounded_box(draw, (48, 48, width - 48, height - 48), radius=24, fill=(20, 20, 24, 250), outline=accent_color, width=3)

    top_bar = Image.new("RGBA", (width - 80, 140), (0, 0, 0, 0))
    draw_top = ImageDraw.Draw(top_bar)
    draw_top.rounded_rectangle((0, 0, width - 80, 140), radius=22, fill=(255, 255, 255, 30))
    image.alpha_composite(top_bar, (40, 50))

    if is_dragon:
        draw.text((width // 2, 92), "UFC DRAGON", fill=(255, 224, 112, 255), anchor="mm", font=_load_font(28, True))
    else:
        draw.text((width // 2, 92), "UFC FIGHTER", fill=(220, 220, 220, 255), anchor="mm", font=_load_font(26, True))

    ovrcode = str(player["ovr"])
    draw.text((width // 2, 165), ovrcode, fill=(255, 255, 255, 255), anchor="mm", font=_load_font(84, True))

    name = player["name"].upper()
    draw.text((width // 2, 265), name, fill=(255, 255, 255, 255), anchor="mm", font=_load_font(42, True))

    if is_dragon:
        badge_color = (255, 210, 70, 255)
        draw.rounded_rectangle((170, 300, 550, 350), radius=18, fill=badge_color)
        draw.text((360, 325), "EXCLUSIVO", fill=(20, 20, 20, 255), anchor="mm", font=_load_font(22, True))
    else:
        draw.rounded_rectangle((220, 300, 500, 350), radius=18, fill=(215, 25, 45, 255))
        draw.text((360, 325), f"{player['position']} • {player['rarity'].upper()}", fill=(255, 255, 255, 255), anchor="mm", font=_load_font(20, True))

    stats_y = 430
    stat_names = ["ATAQUE", "DEFESA", "FÍSICO", "ENERGIA"]
    stat_values = [player["attack"], player["defense"], player["physical"], player["energy"]]
    for index, name in enumerate(stat_names):
        x = 140 + (index % 2) * 240
        y = stats_y + (index // 2) * 160
        draw.rounded_rectangle((x, y, x + 180, y + 110), radius=18, fill=(255, 255, 255, 30), outline=border_color)
        draw.text((x + 90, y + 28), name, fill=(200, 200, 210, 255), anchor="mm", font=_load_font(18, True))
        draw.text((x + 90, y + 72), str(stat_values[index]), fill=(255, 255, 255, 255), anchor="mm", font=_load_font(38, True))

    draw.rounded_rectangle((120, 820, 600, 900), radius=18, fill=(255, 255, 255, 18), outline=accent_color)
    draw.text((360, 860), f"OVR {player['ovr']}", fill=(255, 255, 255, 255), anchor="mm", font=_load_font(28, True))

    if is_dragon:
        draw.text((360, 965), "DRAGÃO DOURADO", fill=(255, 224, 120, 255), anchor="mm", font=_load_font(30, True))
    else:
        draw.text((360, 965), "LUTADOR OFENSIVO", fill=(220, 220, 220, 255), anchor="mm", font=_load_font(30, True))

    image.save(output_path)
    return output_path
