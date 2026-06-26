"""Generate healing tip content for Dhun Detox tip cards."""
import datetime
from .config import CATEGORIES


def get_todays_category():
    idx = datetime.date.today().timetuple().tm_yday % len(CATEGORIES)
    return CATEGORIES[idx]


def generate_tip_content(client, category):
    """Returns (header, tips[(title, detail) x 3], caption)."""
    topic, mood = category
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""You are creating a wellness tip card for @DhunDetox — Indian classical raga healing music channel.

Topic: {topic} for {mood}

Generate 3 practical tips about how "{topic}" helps with "{mood}". These will appear on a visual card.

Rules:
- Each tip has a SHORT TITLE (2-5 words, punchy) and a DETAIL (1 concise sentence, max 15 words)
- Tips should feel like insider knowledge, not generic advice
- Warm, expert tone — like a knowledgeable friend sharing a secret
- Grounded in Indian classical / Hz frequency science (no medical claims)
- Header: short section label (4-6 words)

Output EXACTLY:
HEADER: <4-6 word label like "3 Ways 432Hz Helps You">
TIP_1_TITLE: <2-5 words>
TIP_1_DETAIL: <1 sentence, max 15 words>
TIP_2_TITLE: <2-5 words>
TIP_2_DETAIL: <1 sentence, max 15 words>
TIP_3_TITLE: <2-5 words>
TIP_3_DETAIL: <1 sentence, max 15 words>
CAPTION: <2-sentence IG caption that teases the tips and ends with a soft CTA to save this post>"""
    )

    header, tips, caption = "", [], ""
    for line in response.text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("HEADER:"):
            header = line[7:].strip()
        elif line.startswith("TIP_1_TITLE:"):
            tips.append([line[12:].strip(), ""])
        elif line.startswith("TIP_1_DETAIL:"):
            if tips: tips[-1][1] = line[13:].strip()
        elif line.startswith("TIP_2_TITLE:"):
            tips.append([line[12:].strip(), ""])
        elif line.startswith("TIP_2_DETAIL:"):
            if tips: tips[-1][1] = line[13:].strip()
        elif line.startswith("TIP_3_TITLE:"):
            tips.append([line[12:].strip(), ""])
        elif line.startswith("TIP_3_DETAIL:"):
            if tips: tips[-1][1] = line[13:].strip()
        elif line.startswith("CAPTION:"):
            caption = line[8:].strip()

    if not header:
        header = f"3 Healing Facts About {topic}"
    while len(tips) < 3:
        tips.append(["Listen Intentionally", "30 minutes of raga reduces cortisol by up to 11%."])
    if not caption:
        caption = f"Did you know {topic} can help with {mood}? Save this for your next session. 🎵"

    return header, [tuple(t) for t in tips[:3]], caption
