"""Render Dhun Detox daily raga quote card using PIL.

Style: warm cream (#F5ECD7) background, deep indigo (#1A1F3A) border + text,
warm gold (#D4A857) accents. Matches Dhun Detox brand without needing Madhubani images.
"""
import os
import datetime
from PIL import Image, ImageDraw, ImageFont

from .config import FONTS_DIR, OUTPUT, INDIGO, GOLD, CREAM, GREEN

W, H = 1080, 1920
BORDER = 24   # indigo border thickness all sides


def _load_font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS_DIR, name), size)
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSerif.ttf", size)
        except Exception:
            return ImageFont.load_default()


def _wrap(text, font, max_px, draw):
    words, lines, current = text.split(), [], []
    for word in words:
        test = " ".join(current + [word])
        if draw.textbbox((0, 0), test, font=font)[2] <= max_px:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _today():
    return str(datetime.date.today())


def generate_quote_image(raga, visual_label, quote):
    """Render the daily raga healing quote card. Returns JPG path."""
    img  = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # Deep indigo border (all 4 sides)
    draw.rectangle([0, 0, W - 1, H - 1], outline=INDIGO, width=BORDER)
    # Inner gold hairline border
    IN = BORDER + 6
    draw.rectangle([IN, IN, W - IN - 1, H - IN - 1], outline=GOLD, width=2)

    # Fonts
    f_handle  = _load_font("PlayfairDisplay-Regular.ttf",  38)
    f_label   = _load_font("PlayfairDisplay-Italic.ttf",   52)
    f_raga    = _load_font("PlayfairDisplay-Bold.ttf",     80)
    f_divider = _load_font("PlayfairDisplay-Regular.ttf",  42)
    f_quote   = _load_font("PlayfairDisplay-Italic.ttf",   56)
    f_hz      = _load_font("PlayfairDisplay-Regular.ttf",  38)

    PAD   = BORDER + 60
    TEXT_W = W - PAD * 2

    # Channel handle (top centre)
    hb = draw.textbbox((0, 0), "@DhunDetox", font=f_handle)
    draw.text(((W - (hb[2] - hb[0])) // 2, 72), "@DhunDetox", font=f_handle, fill=GOLD)

    # Visual label (emotional subtitle)
    lb = draw.textbbox((0, 0), visual_label, font=f_label)
    draw.text(((W - (lb[2] - lb[0])) // 2, 160), visual_label, font=f_label, fill=INDIGO)

    # Gold rule
    rule_y = 260
    draw.line([(W // 2 - 80, rule_y), (W // 2 + 80, rule_y)], fill=GOLD, width=3)

    # ✦ ornament
    orn_b = draw.textbbox((0, 0), "✦", font=f_divider)
    draw.text(((W - (orn_b[2] - orn_b[0])) // 2, rule_y + 20), "✦", font=f_divider, fill=GOLD)

    # Raga name (large, centred)
    raga_text = f"Raag {raga}"
    rb = draw.textbbox((0, 0), raga_text, font=f_raga)
    draw.text(((W - (rb[2] - rb[0])) // 2, 380), raga_text, font=f_raga, fill=INDIGO)

    # Gold underline for raga
    raga_w = rb[2] - rb[0]
    draw.line(
        [(W // 2 - raga_w // 2, 490), (W // 2 + raga_w // 2, 490)],
        fill=GOLD, width=4,
    )

    # Quote text (centred, italic)
    q_lines = _wrap(f'"{quote}"', f_quote, TEXT_W, draw)
    q_y     = 560
    for line in q_lines:
        lb = draw.textbbox((0, 0), line, font=f_quote)
        draw.text(((W - (lb[2] - lb[0])) // 2, q_y), line, font=f_quote, fill=INDIGO)
        q_y += 68

    # Bottom gold rule
    bottom_rule_y = H - 280
    draw.line([(W // 2 - 120, bottom_rule_y), (W // 2 + 120, bottom_rule_y)], fill=GOLD, width=2)

    # Sub-label
    sub = "Indian Classical · Raga Healing"
    sb  = draw.textbbox((0, 0), sub, font=f_hz)
    draw.text(((W - (sb[2] - sb[0])) // 2, bottom_rule_y + 20), sub, font=f_hz, fill=(*GOLD,))

    # dhundetox.com at very bottom
    site_b = draw.textbbox((0, 0), "dhundetox.com", font=f_handle)
    draw.text(((W - (site_b[2] - site_b[0])) // 2, H - 140), "dhundetox.com", font=f_handle, fill=INDIGO)

    os.makedirs(OUTPUT, exist_ok=True)
    out = os.path.join(OUTPUT, f"community_{_today()}.jpg")
    img.save(out, "JPEG", quality=95)
    print(f"Community image saved: {out}")
    return out
