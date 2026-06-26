import os

_ROOT     = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONTS_DIR = os.path.join(_ROOT, "assets", "fonts")
OUTPUT    = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")

POST_TIME = "11:00"   # UTC — 4:30 PM IST
POST_DAYS = {2, 3}    # Wed=2, Thu=3

INDIGO = (26, 31, 58)
GOLD   = (212, 168, 87)
CREAM  = (245, 236, 215)

CATEGORIES = [
    ("432Hz music",         "morning calm"),
    ("528Hz frequency",     "cellular healing"),
    ("639Hz music",         "relationships & heart"),
    ("741Hz frequency",     "clarity & expression"),
    ("174Hz frequency",     "pain & tension relief"),
    ("396Hz music",         "guilt & fear release"),
    ("Raag Bhairavi",       "morning healing"),
    ("Raag Yaman",          "evening calm"),
    ("Raag Darbari",        "deep night rest"),
    ("Raag Bhupali",        "joyful uplift"),
    ("Indian classical",    "nervous system"),
    ("Raga meditation",     "focus & clarity"),
    ("Bansuri flute",       "breath & calm"),
    ("Sitar music",         "mind detox"),
    ("Sarangi strings",     "emotional release"),
    ("tanpura drone",       "meditation depth"),
    ("alap in raga",        "deep stillness"),
    ("healing music",       "sleep quality"),
    ("Indian ragas",        "cortisol reset"),
    ("sound healing",       "anxiety relief"),
]

HASHTAGS_IG  = (
    "#dhundetox #ragamusic #indianclassicalmusic #meditationmusic "
    "#healingfrequencies #432hz #soundhealing #anxietyrelief #stressrelief #innerpeace"
)
HASHTAGS_FB  = "#dhundetox #ragamusic #meditationmusic #soundhealing"
