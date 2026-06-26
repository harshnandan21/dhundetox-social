import os

_ROOT     = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONTS_DIR = os.path.join(_ROOT, "assets", "fonts")
OUTPUT    = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")

POST_TIME = "06:00"   # UTC — 11:30 AM IST, daily

# Brand palette
INDIGO  = (26, 31, 58)      # #1A1F3A deep indigo
GOLD    = (212, 168, 87)    # #D4A857 warm gold
CREAM   = (245, 236, 215)   # #F5ECD7 cream ivory
GREEN   = (26, 74, 26)      # #1A4A1A forest green (for accents)
WHITE   = (255, 255, 255)

HASHTAGS_IG  = (
    "#dhundetox #ragamusic #indianclassicalmusic #meditationmusic "
    "#healingfrequencies #432hz #bansurimusic #anxietyrelief #stressrelief "
    "#innerpeace #ragahealing #soundhealing #indianclassical #relaxingmusic"
)
HASHTAGS_FB  = "#dhundetox #ragamusic #meditationmusic #indianclassical"

RAGAS = [
    "Bhairavi", "Bhupali", "Yaman", "Bageshri", "Pahadi",
    "Kedar", "Chandrakauns", "Darbari", "Ahir Bhairav",
    "Madhuvanti", "Vibhas", "Bilaval", "Marwa", "Yaman Kalyan",
]
