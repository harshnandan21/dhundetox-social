"""Post Dhun Detox community quiz/poll (Tue=poll, Sat=quiz) at 10:00 UTC."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
from dotenv import load_dotenv
load_dotenv(os.path.join(_ROOT, ".env"))

import time, datetime, schedule
import cloudinary, cloudinary.uploader
from google import genai

from quiz.src.config import POST_TIME, POST_DAYS, HASHTAGS_IG, HASHTAGS_FB
from quiz.src.quiz_generator import get_post_type, generate_poll, generate_quiz, build_captions
from quiz.src.image_generator import generate_poll_image, generate_quiz_image
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
        print(f"[quiz] Skipping {day_name} — runs Tue + Sat only.")
        return

    post_type = get_post_type()
    question  = ""
    results   = {"instagram": False, "facebook": False}

    print(f"\n{'='*48}")
    print(f"  DhunDetox {post_type.capitalize()} — {day_name}")
    print(f"{'='*48}\n")

    try:
        if post_type == "poll":
            question, options = generate_poll(gemini_client)
            reveal            = ""
            image_path        = generate_poll_image(question, options)
        else:
            question, options, reveal = generate_quiz(gemini_client)
            image_path                = generate_quiz_image(question, options, reveal)

        print(f"Question: {question}")
        reel_path = create_reel(image_path, f"quiz_{post_type}_{datetime.date.today()}_reel.mp4")
        video_url = upload_to_cloudinary(reel_path, folder="dhundetox/quiz")

        ig_caption, fb_caption = build_captions(post_type, question, options, reveal)
        fb_caption += f"\n\n{HASHTAGS_FB}"

        print("\n--- Instagram ---")
        ig_id = _retry("Instagram", post_reel_to_instagram, video_url, ig_caption)
        results["instagram"] = bool(ig_id)
        if ig_id and isinstance(ig_id, str):
            _retry("IG hashtags", post_comment_to_instagram, ig_id, HASHTAGS_IG)
            if post_type == "quiz" and reveal:
                _retry("IG reveal", post_comment_to_instagram, ig_id, f"💡 REVEAL: {reveal}")

        print("\n--- Facebook ---")
        results["facebook"] = bool(_retry("Facebook", post_video_to_facebook, video_url, fb_caption, question[:60]))

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
        f"[DhunDetox] {'✅' if posted else '❌'} {post_type.capitalize()} ({day_name})",
        f"Q: {question}\n\nResults:\n{lines}"
    )


if __name__ == "__main__":
    schedule_only = "--schedule-only" in sys.argv
    if not schedule_only:
        run()
    if "--schedule" in sys.argv or schedule_only:
        schedule.every().day.at(POST_TIME).do(run)
        print(f"[quiz] Scheduler — {POST_TIME} UTC, Tue+Sat only.\n")
        while True:
            schedule.run_pending()
            time.sleep(30)
