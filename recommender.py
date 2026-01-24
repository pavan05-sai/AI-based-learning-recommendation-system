# recommender.py
"""Simple rule‑based AI for LearningAI.
It analyses a user's quiz scores, classifies each subject, and returns
notes & video recommendations for weak subjects.
"""

import sqlite3
import json
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "learning_ai.db")

# Scoring thresholds
WEAK_THRESHOLD = 40
INTERMEDIATE_THRESHOLD = 70

def _get_user_scores(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.id AS subject_id, s.name AS subject_name, q.score
        FROM quizzes q
        JOIN subjects s ON q.subject_id = s.id
        WHERE q.user_id = ?
        """,
        (user_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def _classify_score(score):
    if score < WEAK_THRESHOLD:
        return "weak"
    elif score <= INTERMEDIATE_THRESHOLD:
        return "intermediate"
    else:
        return "strong"

def _fetch_resources_for_subject(subject_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT note_url, video_url FROM resources WHERE subject_id = ?",
        (subject_id,)
    )
    rows = cur.fetchall()
    conn.close()
    # Return lists of notes and videos
    notes = [r["note_url"] for r in rows]
    videos = [r["video_url"] for r in rows]
    return notes, videos

def get_recommendations(user_id):
    """Return a dict mapping subject name to recommendation data.
    Example output:
    {
        "Programming Fundamentals": {
            "level": "weak",
            "notes": ["..."],
            "videos": ["..."]
        },
        ...
    }
    """
    scores = _get_user_scores(user_id)
    recommendations = {}
    for row in scores:
        level = _classify_score(row["score"])
        if level == "weak":
            notes, videos = _fetch_resources_for_subject(row["subject_id"])
        else:
            notes, videos = [], []
        recommendations[row["subject_name"]] = {
            "level": level,
            "score": row["score"],
            "notes": notes,
            "videos": videos,
        }
    return recommendations
