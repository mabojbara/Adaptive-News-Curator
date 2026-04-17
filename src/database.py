import sqlite3
import json
import os
from src.models import UserProfile, Article

DB_PATH = "news_curator.db"

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Store the core user profile attributes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            interests TEXT,
            refined_bio TEXT
        )
    """)
    # Store the history of articles and feedback
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            summary TEXT,
            tags TEXT,
            score INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_profile(profile: UserProfile):
    """Persists the current state of the UserProfile and all article history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Update profile table (single user mode)
    cursor.execute("DELETE FROM profile")
    cursor.execute(
        "INSERT INTO profile (id, interests, refined_bio) VALUES (?, ?, ?)",
        (1, json.dumps(profile.interests), profile.refined_bio)
    )
    
    # Sync article history (Replace everything to ensure consistency)
    cursor.execute("DELETE FROM articles")
    for art in profile.history:
        cursor.execute(
            "INSERT INTO articles (title, url, summary, tags, score) VALUES (?, ?, ?, ?, ?)",
            (art.title, art.url, art.summary, json.dumps(art.tags), art.score)
        )
    
    conn.commit()
    conn.close()

def load_profile():
    """Loads the profile and history from the database if it exists."""
    if not os.path.exists(DB_PATH):
        return None
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT interests, refined_bio FROM profile WHERE id = 1")
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
        
    interests = json.loads(row[0])
    refined_bio = row[1]
    
    cursor.execute("SELECT title, url, summary, tags, score FROM articles")
    article_rows = cursor.fetchall()
    history = [
        Article(title=r[0], url=r[1], summary=r[2], tags=json.loads(r[3]), score=r[4])
        for r in article_rows
    ]
    
    conn.close()
    return UserProfile(interests=interests, refined_bio=refined_bio, history=history)