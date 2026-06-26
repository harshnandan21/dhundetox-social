"""Render Dhun Detox healing tip card images using PIL."""
import os, datetime
from PIL import Image, ImageDraw, ImageFont
from .config import FONTS_DIR, OUTPUT, INDIGO, GOLD, CREAM

W, H   = 1080, 1920
BORDER = 24


def _lf(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS_DIR, name), size)
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSerif.ttf", size)
        except Exception:
            return ImageFont.load_default()


def _wrap(text, font, max_px, draw):
    words, lines, cur = text.split(), [], []
    for w in words:
        test = " ".join(cur + [w])
        if draw.textbbox((0, 0), test, font=font)[2] <= max_px:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def generate_tip_image(header, tips):
    """
    tips: list of 3 (title, detail) tuples.
    Returns path to saved JPEG.
    """
    img  = Image.new("RGBA", (W, H), (*CREAM, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W - 1, H - 1], outline=(*INDIGO, 255), width=BORDER)
    draw.rectangle(
        [BORDER + 6, BORDER + 6, W - BORDER - 7, H - BORDER - 7],
        outline=(*GOLD, 255), width=2
    )

    PAD = BORDER + 70
    CW  = W - PAD * 2

    f_handle  = _lf("PlayfairDisplay-Regular.ttf", 36)
    f_header  = _lf("PlayfairDisplay-Bold.ttf",    56)
    f_title   = _lf("PlayfairDisplay-Bold.ttf",    52)
    f_detail  = _lf("PlayfairDisplay-Regular.ttf", 42)
    f_badge   = _lf("PlayfairDisplay-Bold.ttf",    38)

    image = img.convert("RGB")
    draw  = ImageDraw.Draw(image)

    # Channel handle
    hb = draw.textbbox((0, 0), "@DhunDetox", font=f_handle)
    draw.text(((W - (hb[2] - hb[0])) // 2, 78), "@DhunDetox", font=f_handle, fill=GOLD)

    # Gold divider under handle
    draw.line([(PAD, 128), (W - PAD, 128)], fill=GOLD, width=2)

    # Header block (indigo rectangle)
    tmp_d  = ImageDraw.Draw(Image.new("RGB", (W, H)))
    h_lines = _wrap(header.upper(), f_header, CW - 40, tmp_d)
    HDR_H  = len(h_lines) * 68 + 44

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rectangle([PAD, 150, W - PAD, 150 + HDR_H], fill=(*INDIGO, 255))
    image = Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB")
    draw  = ImageDraw.Draw(image)

    hy = 170
    for line in h_lines:
        lb = draw.textbbox((0, 0), line, font=f_header)
        draw.text(((W - (lb[2] - lb[0])) // 2, hy), line, font=f_header, fill=GOLD)
        hy += 68

    # Tip cards — 3 rows
    CARD_H = 360
    CARD_G = 28
    start_y = 150 + HDR_H + 50
    numbers = ["01", "02", "03"]

    for i, (title, detail) in enumerate(tips):
        cy = start_y + i * (CARD_H + CARD_G)

        layer2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer2).rectangle([PAD, cy, W - PAD, cy + CARD_H], fill=(*INDIGO, 220))
        image = Image.alpha_composite(image.convert("RGBA"), layer2).convert("RGB")
        draw  = ImageDraw.Draw(image)

        # Gold left accent bar
        draw.rectangle([PAD, cy, PAD + 8, cy + CARD_H], fill=GOLD)

        # Number badge
        draw.text((PAD + 38, cy + 30), numbers[i], font=f_badge, fill=GOLD)

        # Title
        title_x = PAD + 90
        title_w = CW - 90
        t_lines = _wrap(title.upper(), f_title, title_w, draw)
        ty = cy + 28
        for tl in t_lines:
            draw.text((title_x, ty), tl, font=f_title, fill=(*CREAM,))
            ty += 64

        # Divider
        draw.line([(PAD + 90, ty + 4), (W - PAD - 20, ty + 4)], fill=(*GOLD, 90), width=1)

        # Detail text
        d_lines = _wrap(detail, f_detail, CW - 90, draw)
        dy = ty + 18
        for dl in d_lines:
            draw.text((title_x, dy), dl, font=f_detail, fill=(*CREAM, 200))
            dy += 52

    # Footer
    footer = "🎵 Save this • Follow @DhunDetox"
    fb = draw.textbbox((0, 0), footer, font=f_handle)
    draw.text(((W - (fb[2] - fb[0])) // 2, H - 80), footer, font=f_handle, fill=INDIGO)

    os.makedirs(OUTPUT, exist_ok=True)
    out = os.path.join(OUTPUT, f"tips_{datetime.date.today()}.jpg")
    image.save(out, "JPEG", quality=95)
    print(f"Tips image saved: {out}")
    return out
