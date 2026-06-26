"""Post a daily raga healing quote to Instagram and Facebook.

Schedule: 06:00 UTC (11:30 AM IST) every day.

Usage:
    python community/scripts/post_community.py                  # post immediately
    python community/scripts/post_community.py --schedule       # post now + repeat daily
    python community/scripts/post_community.py --schedule-only  # Railway: skip immediate
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(_ROOT, ".env"))

import time, datetime, schedule
import cloudinary, cloudinary.uploader
from google import genai

from community.src.config import POST_TIME, HASHTAGS_IG, HASHTAGS_FB
from community.src.content_generator import get_todays_raga, generate_raga_quote
from community.src.image_generator import generate_quote_image
from src.reel_generator import create_reel, upload_to_cloudinary
from src.poster import post_reel_to_instagram, post_comment_to_instagram, post_video_to_facebook
from src.alerts import send_alert

if hasattr(time, "tzset"):
    time.tzset()

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


def _retry(label, fn, *args, retries=1, delay=60):
    for attempt in range(retries + 1):
        try:
            r = fn(*args)
            return r if r is not None else True
        except Exception as e:
            if attempt < retries:
                print(f"{label} failed, retrying in {delay}s: {e}")
                time.sleep(delay)
            else:
                import traceback; traceback.print_exc()
                print(f"{label} failed after {retries+1} attempts: {e}")
    return False


def run():
    raga = get_todays_raga()
    print(f"\n{'='*48}")
    print(f"  DhunDetox Community Post — Raag {raga}")
    print(f"{'='*48}\n")

    results = {"instagram": False, "facebook": False}
    raga_name = ""

    try:
        raga_name, visual_label, quote, caption = generate_raga_quote(gemini_client, raga)
        print(f"Visual label : {visual_label}")
        print(f"Quote        : {quote[:80]}...")

        image_path = generate_quote_image(raga_name, visual_label, quote)
        reel_path  = create_reel(image_path, f"community_{datetime.date.today()}_reel.mp4")
        video_url  = upload_to_cloudinary(reel_path, folder="dhundetox/community")

        ig_caption = f"{caption}\n\n🎵 Listen on YouTube — link in bio."
        fb_caption = f"{caption}\n\n🎵 Full raga sessions on YouTube — Dhun Detox.\n\n{HASHTAGS_FB}"

        print("\n--- Instagram ---")
        ig_id = _retry("Instagram", post_reel_to_instagram, video_url, ig_caption)
        results["instagram"] = bool(ig_id)
        if ig_id and isinstance(ig_id, str):
            _retry("IG hashtags", post_comment_to_instagram, ig_id, HASHTAGS_IG)

        print("\n--- Facebook ---")
        results["facebook"] = bool(_retry(
            "Facebook", post_video_to_facebook, video_url, fb_caption, f"Raag {raga_name} — Healing Music"
        ))

    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"\nFatal error: {e}")

    posted = [p for p, ok in results.items() if ok]
    failed = [p for p, ok in results.items() if not ok]
    lines  = "\n".join(f"  ✅ {p.capitalize()}" for p in posted)
    lines += ("\n" + "\n".join(f"  ❌ {p.capitalize()}" for p in failed)) if failed else ""

    print(f"\n{'='*48}")
    for p, ok in results.items():
        print(f"  {p.capitalize():12s} → {'Posted' if ok else 'FAILED'}")
    print(f"{'='*48}\n")

    subject = (
        f"[DhunDetox] ✅ Community post (Raag {raga_name}) — {', '.join(p.capitalize() for p in posted)}"
        if posted else
        f"[DhunDetox] ❌ Community post (Raag {raga_name}) FAILED"
    )
    send_alert(subject, f"Raga: {raga_name}\nQuote: {quote}\n\nResults:\n{lines}")


if __name__ == "__main__":
    schedule_only = "--schedule-only" in sys.argv
    if not schedule_only:
        run()
    if "--schedule" in sys.argv or schedule_only:
        schedule.every().day.at(POST_TIME).do(run)
        print(f"[community] Scheduler — daily at {POST_TIME} UTC.\n")
        while True:
            schedule.run_pending()
            time.sleep(30)
