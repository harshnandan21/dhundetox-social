#!/bin/bash
set -e

mkdir -p assets/fonts assets/music output community/output quiz/output tips/output

# 00:30 UTC (6:00 AM IST) — Process shorts/reels from queue (posted by local pipeline)
echo "[startup] Starting shorts queue processor (00:30 UTC)..."
python shorts/scripts/post_shorts.py --schedule-only &

# 06:00 UTC (11:30 AM IST) — Daily raga healing quote → IG + FB
echo "[startup] Starting community post scheduler (06:00 UTC)..."
python community/scripts/post_community.py --schedule-only &

# 10:00 UTC (3:30 PM IST) — Quiz/poll (Tue=poll, Sat=quiz)
echo "[startup] Starting quiz/poll scheduler (10:00 UTC)..."
python quiz/scripts/post_quiz.py --schedule-only &

# 11:00 UTC (4:30 PM IST) — Healing tip post (Wed+Thu)
echo "[startup] Starting tips scheduler (11:00 UTC)..."
python tips/scripts/post_tips.py --schedule-only &

wait
