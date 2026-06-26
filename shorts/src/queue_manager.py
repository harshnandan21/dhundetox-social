"""Read and write content/queue.json via GitHub API."""
import os, json, base64, datetime
import requests

GITHUB_API = "https://api.github.com"


def _headers():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set")
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _repo():
    owner = os.getenv("GITHUB_OWNER", "harshnandan21")
    repo  = os.getenv("GITHUB_REPO",  "dhundetox-social")
    return owner, repo


def _get_file(path="content/queue.json"):
    owner, repo = _repo()
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    r = requests.get(url, headers=_headers(), timeout=30)
    r.raise_for_status()
    data = r.json()
    content = json.loads(base64.b64decode(data["content"]).decode())
    return content, data["sha"]


def _put_file(content, sha, path="content/queue.json", message="chore: update queue"):
    owner, repo = _repo()
    url  = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    body = {
        "message": message,
        "content": base64.b64encode(
            json.dumps(content, indent=2, ensure_ascii=False).encode()
        ).decode(),
        "sha": sha,
    }
    r = requests.put(url, headers=_headers(), json=body, timeout=30)
    r.raise_for_status()
    return r.json()


def get_pending_for_now():
    """Return list of queue items whose post_at <= now and status=='pending'."""
    try:
        data, _ = _get_file()
        now   = datetime.datetime.utcnow()
        items = []
        for item in data.get("queue", []):
            if item.get("status") != "pending":
                continue
            post_at = datetime.datetime.fromisoformat(item["post_at"])
            if post_at <= now:
                items.append(item)
        return items
    except Exception as e:
        print(f"[queue] Failed to read queue: {e}")
        return []


def mark_done(item_id, error=None):
    """Mark a queue item as done (or failed)."""
    try:
        data, sha = _get_file()
        for item in data.get("queue", []):
            if item.get("id") == item_id:
                item["status"] = "failed" if error else "done"
                item["processed_at"] = datetime.datetime.utcnow().isoformat()
                if error:
                    item["error"] = str(error)
                break
        _put_file(data, sha, message=f"chore: mark {item_id} {'failed' if error else 'done'}")
        print(f"[queue] Marked {item_id} as {'failed' if error else 'done'}")
    except Exception as e:
        print(f"[queue] Failed to mark {item_id}: {e}")


def push_item(item: dict):
    """Add a new item to the queue. item must have: id, video_url, cover_url, caption, title, post_at, status='pending'."""
    try:
        data, sha = _get_file()
        data.setdefault("queue", []).append(item)
        _put_file(data, sha, message=f"chore: queue {item.get('id', 'item')}")
        print(f"[queue] Pushed {item.get('id')} → post_at={item.get('post_at')}")
    except Exception as e:
        print(f"[queue] Failed to push item: {e}")
        raise
