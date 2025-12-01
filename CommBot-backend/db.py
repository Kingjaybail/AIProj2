import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

# Path to SQLite database
DB_PATH = Path("database/app.db")


# -----------------------------
# DATABASE CONNECTION & INIT
# -----------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # REQUIRED for cascading delete etc.
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Initialize the SQLite database with user + chats tables."""
    conn = get_conn()

    conn.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            messages TEXT NOT NULL,      -- JSON list of messages
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )

    conn.commit()
    conn.close()


# -----------------------------
# USER ACCOUNT FUNCTIONS
# -----------------------------
def create_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Create a new user. Returns user dict or None if email exists."""
    conn = get_conn()


    try:
        conn.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, password),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return None  # Email already exists

    # Return created user
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return dict(user)


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Validate user login."""
    conn = get_conn()

    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()

    if not user:
        return None

    if password == user["password"]:
        return dict(user)

    return None


# -----------------------------
# CHAT FUNCTIONS
# -----------------------------
def create_chat(user_id: int, title: str = "New Chat") -> Dict[str, Any]:
    """Create a new chat session for a user."""
    conn = get_conn()

    conn.execute(
        "INSERT INTO chats (user_id, title, messages) VALUES (?, ?, ?)",
        (user_id, title, json.dumps([])),
    )
    conn.commit()

    chat = conn.execute(
        "SELECT * FROM chats WHERE rowid = last_insert_rowid()"
    ).fetchone()

    return dict(chat)


def append_message(chat_id: int, role: str, text: str, sources=None):
    conn = get_conn()

    chat = conn.execute(
        "SELECT * FROM chats WHERE id = ?", (chat_id,)
    ).fetchone()

    if not chat:
        return []

    messages = json.loads(chat["messages"])

    messages.append({
        "role": role,
        "text": text,
        "sources": sources or []
    })

    conn.execute(
        """
        UPDATE chats
        SET messages = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (json.dumps(messages), chat_id),
    )
    conn.commit()

    return messages




def get_user_chats(user_id: int) -> List[Dict[str, Any]]:
    """List all chats belonging to a user."""
    conn = get_conn()

    rows = conn.execute(
        """
        SELECT id, title, updated_at
        FROM chats
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (user_id,),
    ).fetchall()

    return [dict(r) for r in rows]


def get_chat(chat_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a chat by ID."""
    conn = get_conn()
    chat = conn.execute(
        "SELECT * FROM chats WHERE id = ?", (chat_id,)
    ).fetchone()

    return dict(chat) if chat else None


def delete_chat(chat_id: int):
    conn = get_conn()
    print(chat_id)
    conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()


def debug_print():
    """Useful for verifying DB contents."""
    conn = get_conn()

    print("\n=== USERS ===")
    for row in conn.execute("SELECT * FROM users").fetchall():
        print(dict(row))

    print("\n=== CHATS ===")
    for row in conn.execute("SELECT * FROM chats").fetchall():
        print(dict(row))

    conn.close()

def update_chat_title(chat_id: int, title: str):
    conn = get_conn()
    conn.execute(
        """
        UPDATE chats
        SET title = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (title, chat_id),
    )
    conn.commit()