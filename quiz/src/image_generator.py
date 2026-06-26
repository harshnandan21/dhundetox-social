"""Render Dhun Detox quiz/poll card images using PIL."""
import os, datetime
from PIL import Image, ImageDraw, ImageFont
from .config import FONTS_DIR, OUTPUT, INDIGO, GOLD, CREAM

W, H   = 1080, 1920
BORDER = 24
CARD   = (*INDIGO, 220)   # deep indigo card (RGBA)
OPT    = (255, 255, 255, 28)


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


def _add_card(img, x, y, w, h, rgba):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rectangle([x, y, x + w, y + h], fill=rgba)
    return Image.alpha_composite(img, layer)


def _today():
    return str(datetime.date.today())


def _base():
    img  = Image.new("RGBA", (W, H), (*CREAM, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W - 1, H - 1], outline=(*INDIGO, 255), width=BORDER)
    draw.rectangle([BORDER + 6, BORDER + 6, W - BORDER - 7, H - BORDER - 7], outline=(*GOLD, 255), width=2)
    return img


def generate_poll_image(question, options):
    img = _base()
    PAD = BORDER + 60
    CW  = W - PAD * 2
    tmp = img.convert("RGB")
    d   = ImageDraw.Draw(tmp)

    f_handle = _lf("PlayfairDisplay-Regular.ttf", 36)
    f_label  = _lf("PlayfairDisplay-Italic.ttf",  44)
    f_q      = _lf("PlayfairDisplay-Bold.ttf",    60)
    f_opt    = _lf("PlayfairDisplay-Regular.ttf", 50)
    f_cta    = _lf("PlayfairDisplay-Italic.ttf",  46)

    q_lines = _wrap(question, f_q, CW - 60, d)
    Q_H     = len(q_lines) * 76 + 60
    OPT_H, OPT_G = 108, 18

    img = _add_card(img, PAD, 240, CW, Q_H, CARD)
    for i in range(4):
        img = _add_card(img, PAD, 240 + Q_H + 36 + i * (OPT_H + OPT_G), CW, OPT_H, OPT)

    image = img.convert("RGB")
    draw  = ImageDraw.Draw(image)

    hb = draw.textbbox((0, 0), "@DhunDetox", font=f_handle)
    draw.text(((W - (hb[2] - hb[0])) // 2, 72), "@DhunDetox", font=f_handle, fill=GOLD)

    lb = draw.textbbox((0, 0), "✦  COMMUNITY POLL  ✦", font=f_label)
    draw.text(((W - (lb[2] - lb[0])) // 2, 155), "✦  COMMUNITY POLL  ✦", font=f_label, fill=INDIGO)

    qy = 268
    for line in q_lines:
        lb = draw.textbbox((0, 0), line, font=f_q)
        draw.text(((W - (lb[2] - lb[0])) // 2, qy), line, font=f_q, fill=(*CREAM,))
        qy += 76

    cta_y = 240 + Q_H + 8
    ctab  = draw.textbbox((0, 0), "Drop your answer below 👇", font=f_cta)
    draw.text(((W - (ctab[2] - ctab[0])) // 2, cta_y), "Drop your answer below 👇", font=f_cta, fill=GOLD)

    opts_start = 240 + Q_H + 36
    for i, opt in enumerate(options):
        oy = opts_start + i * (OPT_H + OPT_G)
        draw.text((PAD + 44, oy + OPT_H // 2), opt, font=f_opt, fill=INDIGO, anchor="lm")

    os.makedirs(OUTPUT, exist_ok=True)
    out = os.path.join(OUTPUT, f"quiz_poll_{_today()}.jpg")
    image.save(out, "JPEG", quality=95)
    print(f"Poll image saved: {out}")
    return out


def generate_quiz_image(question, options, reveal):
    img = _base()
    PAD = BORDER + 60
    CW  = W - PAD * 2
    tmp = img.convert("RGB")
    d   = ImageDraw.Draw(tmp)

    f_handle = _lf("PlayfairDisplay-Regular.ttf", 36)
    f_label  = _lf("PlayfairDisplay-Bold.ttf",    40)
    f_q      = _lf("PlayfairDisplay-Bold.ttf",    58)
    f_opt    = _lf("PlayfairDisplay-Regular.ttf", 46)
    f_badge  = _lf("PlayfairDisplay-Bold.ttf",    36)
    f_reveal = _lf("PlayfairDisplay-Italic.ttf",  40)

    q_lines = _wrap(question, f_q, CW - 60, d)
    Q_H     = len(q_lines) * 72 + 60
    OPT_H, OPT_G = 100, 14

    rev_lines = _wrap(reveal, f_reveal, CW - 60, d)
    REV_H     = len(rev_lines) * 52 + 44

    q_y    = 220
    opts_y = q_y + Q_H + 24
    rev_y  = opts_y + 4 * (OPT_H + OPT_G) + 30

    img = _add_card(img, PAD, q_y, CW, Q_H, CARD)
    for i in range(4):
        img = _add_card(img, PAD, opts_y + i * (OPT_H + OPT_G), CW, OPT_H, OPT)
    if rev_y + REV_H < H - 60:
        img = _add_card(img, PAD, rev_y, CW, REV_H, CARD)

    image = img.convert("RGB")
    draw  = ImageDraw.Draw(image)

    hb = draw.textbbox((0, 0), "@DhunDetox", font=f_handle)
    draw.text(((W - (hb[2] - hb[0])) // 2, 72), "@DhunDetox", font=f_handle, fill=GOLD)

    lb = draw.textbbox((0, 0), "✦  RAGA QUIZ  ✦", font=f_label)
    draw.text(((W - (lb[2] - lb[0])) // 2, 148), "✦  RAGA QUIZ  ✦", font=f_label, fill=INDIGO)

    qy = q_y + 28
    for line in q_lines:
        lb = draw.textbbox((0, 0), line, font=f_q)
        draw.text(((W - (lb[2] - lb[0])) // 2, qy), line, font=f_q, fill=(*CREAM,))
        qy += 72

    letters = ["A", "B", "C", "D"]
    for i, opt in enumerate(options):
        oy  = opts_y + i * (OPT_H + OPT_G)
        mid = oy + OPT_H // 2
        draw.text((PAD + 44, mid), letters[i], font=f_badge, fill=GOLD, anchor="mm")
        draw.line([(PAD + 72, oy + 16), (PAD + 72, oy + OPT_H - 16)], fill=(*GOLD, 80), width=1)
        draw.text((PAD + 92, mid), opt, font=f_opt, fill=INDIGO, anchor="lm")

    if rev_y + REV_H < H - 60:
        ry = rev_y + 18
        for line in rev_lines:
            lb = draw.textbbox((0, 0), line, font=f_reveal)
            draw.text(((W - (lb[2] - lb[0])) // 2, ry), line, font=f_reveal, fill=(*CREAM,))
            ry += 52

    os.makedirs(OUTPUT, exist_ok=True)
    out = os.path.join(OUTPUT, f"quiz_card_{_today()}.jpg")
    image.save(out, "JPEG", quality=95)
    print(f"Quiz image saved: {out}")
    return out
