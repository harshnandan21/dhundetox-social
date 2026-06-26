"""Read content/queue.json and post due shorts to Instagram + Facebook."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
from dotenv import load_dotenv
load_dotenv(os.path.join(_ROOT, ".env"))

import time, schedule
import cloudinary, cloudinary.uploader

from shorts.src.queue_manager import get_pending_for_now, mark_done
from src.poster import post_reel_to_instagram, post_comment_to_instagram, post_video_to_facebook
from src.alerts import send_alert

if hasattr(time, "tzset"):
    time.tzset()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

POST_TIME = "00:30"   # UTC — check queue 30 min after music pipeline upload slot

HASHTAGS_IG = (
    "#dhundetox #ragamusic #indianclassicalmusic #meditationmusic "
    "#healingfrequencies #432hz #soundhealing #anxietyrelief #stressrelief #bansurimusic"
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
    return False


def process_item(item):
    item_id   = item.get("id", "unknown")
    video_url = item.get("video_url")
    cover_url = item.get("cover_url")
    caption   = item.get("caption", "")
    title     = item.get("title", "Dhun Detox")
    results   = {"instagram": False, "facebook": False}

    print(f"\n  Processing: {item_id}")
    print(f"  Title: {title}")
    print(f"  Video: {video_url[:60]}...")

    try:
        print("  --- Instagram Reel ---")
        ig_id = _retry("Instagram", post_reel_to_instagram, video_url, caption, cover_url)
        results["instagram"] = bool(ig_id)
        if ig_id and isinstance(ig_id, str):
            _retry("IG hashtags", post_comment_to_instagram, ig_id, HASHTAGS_IG)

        print("  --- Facebook Video ---")
        results["facebook"] = bool(
            _retry("Facebook", post_video_to_facebook, video_url, caption, title[:60])
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        mark_done(item_id, error=e)
        return

    mark_done(item_id)

    posted = [p for p, ok in results.items() if ok]
    failed = [p for p, ok in results.items() if not ok]
    lines  = "\n".join(f"  ✅ {p.capitalize()}" for p in posted)
    lines += ("\n" + "\n".join(f"  ❌ {p.capitalize()}" for p in failed)) if failed else ""

    send_alert(
        f"[DhunDetox] {'✅' if posted else '❌'} Short posted: {title[:40]}",
        f"ID: {item_id}\n\nResults:\n{lines}"
    )


def run():
    print(f"\n{'='*48}")
    print(f"  DhunDetox Shorts Queue Check")
    print(f"{'='*48}")

    items = get_pending_for_now()
    if not items:
        print("  No pending items due right now.")
        return

    print(f"  Found {len(items)} item(s) to post.\n")
    for item in items:
        process_item(item)

    print(f"\n{'='*48}\n")


if __name__ == "__main__":
    schedule_only = "--schedule-only" in sys.argv
    if not schedule_only:
        run()
    if "--schedule" in sys.argv or schedule_only:
        schedule.every().day.at(POST_TIME).do(run)
        print(f"[shorts] Scheduler — {POST_TIME} UTC daily.\n")
        while True:
            schedule.run_pending()
            time.sleep(30)
