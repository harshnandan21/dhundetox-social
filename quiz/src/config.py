import os

_ROOT     = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONTS_DIR = os.path.join(_ROOT, "assets", "fonts")
OUTPUT    = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")

POST_TIME = "10:00"   # UTC — 3:30 PM IST
POST_DAYS = {1, 5}    # Tue=1 (poll), Sat=5 (quiz)

INDIGO = (26, 31, 58)
GOLD   = (212, 168, 87)
CREAM  = (245, 236, 215)

HASHTAGS_IG  = (
    "#dhundetox #ragamusic #indianclassicalmusic #meditationmusic "
    "#healingfrequencies #soundhealing #raga #classicalmusic"
)
HASHTAGS_FB  = "#dhundetox #ragamusic #indianclassical"
