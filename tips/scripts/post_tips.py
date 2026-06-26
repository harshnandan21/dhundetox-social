"""Post Dhun Detox healing tip card (Wed + Thu) at 11:00 UTC."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
from dotenv import load_dotenv
load_dotenv(os.path.join(_ROOT, ".env"))

import time, datetime, schedule
import cloudinary, cloudinary.uploader
from google import genai

from tips.src.config import POST_TIME, POST_DAYS, HASHTAGS_IG, HASHTAGS_FB
from tips.src.content_generator import get_todays_category, generate_tip_content
from tips.src.image_generator import generate_tip_image
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

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


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
    return False


def run():
    today    = datetime.date.today().weekday()
    day_name = DAY_NAMES[today]
    if today not in POST_DAYS:
        print(f"[tips] Skipping {day_name} — runs Wed + Thu only.")
        return

    category = get_todays_category()
    topic, mood = category
    results = {"instagram": False, "facebook": False}

    print(f"\n{'='*48}")
    print(f"  DhunDetox Healing Tips — {day_name}")
    print(f"  Topic: {topic} for {mood}")
    print(f"{'='*48}\n")

    try:
        header, tips, caption = generate_tip_content(gemini_client, category)
        print(f"Header: {header}")
        for i, (t, d) in enumerate(tips, 1):
            print(f"  Tip {i}: {t} — {d}")

        image_path = generate_tip_image(header, tips)
        reel_path  = create_reel(image_path, f"tips_{datetime.date.today()}_reel.mp4")
        video_url  = upload_to_cloudinary(reel_path, folder="dhundetox/tips")

        ig_caption = f"{caption}\n\n{header}\n"
        for i, (t, d) in enumerate(tips, 1):
            ig_caption += f"\n{i}. {t}\n   {d}"
        ig_caption += "\n\n💾 Save this for your next session."

        fb_caption = ig_caption + f"\n\n{HASHTAGS_FB}"

        print("\n--- Instagram ---")
        ig_id = _retry("Instagram", post_reel_to_instagram, video_url, ig_caption)
        results["instagram"] = bool(ig_id)
        if ig_id and isinstance(ig_id, str):
            _retry("IG hashtags", post_comment_to_instagram, ig_id, HASHTAGS_IG)

        print("\n--- Facebook ---")
        results["facebook"] = bool(
            _retry("Facebook", post_video_to_facebook, video_url, fb_caption, header[:60])
        )

    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"\nFatal: {e}")

    posted = [p for p, ok in results.items() if ok]
    failed = [p for p, ok in results.items() if not ok]
    lines  = "\n".join(f"  ✅ {p.capitalize()}" for p in posted)
    lines += ("\n" + "\n".join(f"  ❌ {p.capitalize()}" for p in failed)) if failed else ""

    print(f"\n{'='*48}")
    for p, ok in results.items():
        print(f"  {p.capitalize():12s} → {'Posted' if ok else 'FAILED'}")
    print(f"{'='*48}\n")

    send_alert(
        f"[DhunDetox] {'✅' if posted else '❌'} Tips Card ({day_name})",
        f"Topic: {topic} for {mood}\nHeader: {header}\n\nResults:\n{lines}"
    )


if __name__ == "__main__":
    schedule_only = "--schedule-only" in sys.argv
    if not schedule_only:
        run()
    if "--schedule" in sys.argv or schedule_only:
        schedule.every().day.at(POST_TIME).do(run)
        print(f"[tips] Scheduler — {POST_TIME} UTC, Wed+Thu only.\n")
        while True:
            schedule.run_pending()
            time.sleep(30)
