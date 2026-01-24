# db_init.py

"""Create SQLite database and seed initial data for LearningAI.
The script defines tables and loads JSON files containing subject definitions,
roadmaps, and resource links for all branches.
"""

import sqlite3
import os
import json

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "learning_ai.db")

# Paths to seed JSON files
SUBJECTS_JSON = os.path.join(BASE_DIR, "data", "subjects.json")
RESOURCES_JSON = os.path.join(BASE_DIR, "data", "resources.json")

def init_db():
    # Remove existing DB to ensure clean state with new seed data
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Removed existing database.")
        except PermissionError:
            print("Could not remove existing database (might be open). Proceeding to use existing file...")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Enable foreign keys
    c.execute('PRAGMA foreign_keys = ON;')
    
    # Create Tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            branch TEXT NOT NULL,
            semester INTEGER NOT NULL
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch TEXT NOT NULL,
            semester INTEGER NOT NULL,
            name TEXT NOT NULL,
            roadmap_json TEXT NOT NULL
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            note_url TEXT NOT NULL,
            video_url TEXT NOT NULL,
            FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            level TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        );
    ''')
    conn.commit()

    # Load seed data
    print("Seeding subjects...")
    if os.path.exists(SUBJECTS_JSON):
        with open(SUBJECTS_JSON, "r", encoding="utf-8") as f:
            subjects = json.load(f)
        
        # Use a set to avoid duplicate insertions if running multiple times (though we dropped DB mostly)
        for sub in subjects:
            # Check overlap if we didn't drop DB
            c.execute("SELECT id FROM subjects WHERE branch=? AND semester=? AND name=?", 
                      (sub["branch"], sub["semester"], sub["name"]))
            if c.fetchone() is None:
                c.execute(
                    "INSERT INTO subjects (branch, semester, name, roadmap_json) VALUES (?,?,?,?)",
                    (sub["branch"], sub["semester"], sub["name"], json.dumps(sub["roadmap"]))
                )
        conn.commit()

    print("Seeding resources...")
    if os.path.exists(RESOURCES_JSON):
        with open(RESOURCES_JSON, "r", encoding="utf-8") as f:
            resources = json.load(f)
        
        for res in resources:
            # Resolve subject_id
            c.execute(
                "SELECT id FROM subjects WHERE branch=? AND semester=? AND name=?",
                (res["branch"], res["semester"], res["subject"]))
            row = c.fetchone()
            if row:
                subject_id = row[0]
                # Check exist
                c.execute("SELECT id FROM resources WHERE subject_id=? AND note_url=?", (subject_id, res["note_url"]))
                if c.fetchone() is None:
                    c.execute(
                        "INSERT INTO resources (subject_id, note_url, video_url) VALUES (?,?,?)",
                        (subject_id, res["note_url"], res["video_url"]))
        conn.commit()
    
    conn.close()
    print("Database initialized successfully at", DB_PATH)

if __name__ == "__main__":
    init_db()
