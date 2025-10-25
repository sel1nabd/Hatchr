"""
Database models and utilities for Hatchr
SQLite database with async support via aiosqlite
"""

import aiosqlite
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "hatchr.db"


async def init_database():
    """Initialize database and create tables if they don't exist"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Create users table for Concordium wallet authentication
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address TEXT UNIQUE NOT NULL,
                name TEXT,
                age INTEGER,
                country_of_residence TEXT,
                date_of_birth TEXT,
                created_at TEXT NOT NULL,
                last_login TEXT NOT NULL
            )
        """)

        # Create sessions table for auth tokens
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                auth_token TEXT UNIQUE NOT NULL,
                challenge TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Create index for faster lookups
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_wallet_address
            ON users(wallet_address)
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_auth_token
            ON sessions(auth_token)
        """)

        await db.commit()
        print(f"✅ Database initialized at {DATABASE_PATH}")


async def get_user_by_wallet(wallet_address: str) -> Optional[Dict[str, Any]]:
    """Get user by Concordium wallet address"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE wallet_address = ?",
            (wallet_address,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def create_user(
    wallet_address: str,
    name: Optional[str] = None,
    age: Optional[int] = None,
    country_of_residence: Optional[str] = None,
    date_of_birth: Optional[str] = None
) -> Dict[str, Any]:
    """Create new user with Concordium wallet address"""
    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO users (wallet_address, name, age, country_of_residence,
                             date_of_birth, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (wallet_address, name, age, country_of_residence, date_of_birth, now, now)
        )
        await db.commit()
        user_id = cursor.lastrowid

        return {
            "id": user_id,
            "wallet_address": wallet_address,
            "name": name,
            "age": age,
            "country_of_residence": country_of_residence,
            "date_of_birth": date_of_birth,
            "created_at": now,
            "last_login": now
        }


async def update_user_login(wallet_address: str) -> None:
    """Update last login timestamp for user"""
    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE users SET last_login = ? WHERE wallet_address = ?",
            (now, wallet_address)
        )
        await db.commit()


async def create_session(
    user_id: int,
    auth_token: str,
    challenge: str,
    expires_in_hours: int = 24
) -> Dict[str, Any]:
    """Create authentication session for user"""
    from datetime import timedelta

    now = datetime.utcnow()
    expires_at = (now + timedelta(hours=expires_in_hours)).isoformat()
    created_at = now.isoformat()

    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO sessions (user_id, auth_token, challenge, expires_at, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, auth_token, challenge, expires_at, created_at)
        )
        await db.commit()
        session_id = cursor.lastrowid

        return {
            "id": session_id,
            "user_id": user_id,
            "auth_token": auth_token,
            "expires_at": expires_at,
            "created_at": created_at
        }


async def get_session_by_token(auth_token: str) -> Optional[Dict[str, Any]]:
    """Get session by auth token"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT s.*, u.wallet_address, u.name, u.age, u.country_of_residence
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.auth_token = ? AND s.expires_at > ?
            """,
            (auth_token, datetime.utcnow().isoformat())
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def invalidate_session(auth_token: str) -> None:
    """Delete/invalidate a session"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM sessions WHERE auth_token = ?",
            (auth_token,)
        )
        await db.commit()


async def cleanup_expired_sessions() -> int:
    """Remove expired sessions from database"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM sessions WHERE expires_at < ?",
            (datetime.utcnow().isoformat(),)
        )
        await db.commit()
        return cursor.rowcount
