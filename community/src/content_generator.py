"""Generate daily raga healing quote content using Gemini."""
import datetime
import random
from .config import RAGAS


def get_todays_raga():
    day = datetime.date.today().timetuple().tm_yday
    return RAGAS[day % len(RAGAS)]


def generate_raga_quote(client, raga=None):
    """Generate a raga healing quote card. Returns (raga, visual_label, quote, caption)."""
    if not raga:
        raga = get_todays_raga()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""You are creating a daily healing quote card for @DhunDetox — an Indian classical raga healing music channel on Instagram.

Today's raga: {raga}

Generate one deeply evocative quote about this raga's healing quality. The quote should:
- Be 1-2 sentences, poetic and emotionally resonant
- Reference the raga's specific mood, time of day, or healing quality
- Feel like something a classical musician or Ayurvedic healer would say
- NOT mention apps, streaming, or modern technology

Also generate:
- VISUAL_LABEL: 3-4 words that capture the emotional essence (e.g. "For the restless mind", "When words are not enough")
- CAPTION: 55-70 word Instagram caption. First line = raga name + key benefit (no emoji, keyword-first). Then 2-3 short emotional lines. End with one question that invites reflection. No hashtags.

Output EXACTLY this format:
RAGA: {raga}
VISUAL_LABEL: <3-4 words>
QUOTE: <1-2 sentence healing quote, no quotation marks>
CAPTION: <55-70 word caption, no hashtags>"""
    )

    fields = {"raga": raga, "visual_label": "", "quote": "", "caption": ""}
    caption_lines = []
    current = None

    for line in response.text.strip().splitlines():
        line = line.strip()
        if not line and current != "caption":
            continue
        if line.startswith("RAGA:"):
            fields["raga"] = line[5:].strip()
            current = None
        elif line.startswith("VISUAL_LABEL:"):
            fields["visual_label"] = line[13:].strip().replace("**", "")
            current = None
        elif line.startswith("QUOTE:"):
            fields["quote"] = line[6:].strip().replace("**", "")
            current = None
        elif line.startswith("CAPTION:"):
            current = "caption"
            first = line[8:].strip().replace("**", "")
            if first:
                caption_lines.append(first)
        elif current == "caption":
            caption_lines.append(line.replace("**", ""))

    if caption_lines:
        while caption_lines and not caption_lines[-1]:
            caption_lines.pop()
        fields["caption"] = "\n".join(caption_lines)

    if not fields["visual_label"]:
        fields["visual_label"] = "For a restless mind"
    if not fields["quote"]:
        fields["quote"] = f"Raag {raga} speaks where words fall silent — let it carry what you cannot say."
    if not fields["caption"]:
        fields["caption"] = f"Raag {raga} — ancient healing for the modern mind.\n\nWhat do you carry that music might ease tonight?"

    return fields["raga"], fields["visual_label"], fields["quote"], fields["caption"]
