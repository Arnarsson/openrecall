import sqlite3
import os
from collections import namedtuple
from datetime import datetime
import numpy as np
from typing import Any, Dict, List, Optional, Tuple

from openrecall.config import db_path, screenshots_path

# Define the structure of a database entry using namedtuple
Entry = namedtuple("Entry", ["id", "app", "title", "text", "timestamp", "embedding"])


def create_db() -> None:
    """
    Creates the SQLite database and the 'entries' table if they don't exist.

    The table schema includes columns for an auto-incrementing ID, application name,
    window title, extracted text, timestamp, and text embedding.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS entries (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       app TEXT,
                       title TEXT,
                       text TEXT,
                       timestamp INTEGER UNIQUE,
                       embedding BLOB
                   )"""
            )
            # Add index on timestamp for faster lookups
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON entries (timestamp)"
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error during table creation: {e}")


def get_all_entries() -> List[Entry]:
    """
    Retrieves all entries from the database.

    Returns:
        List[Entry]: A list of all entries as Entry namedtuples.
                     Returns an empty list if the table is empty or an error occurs.
    """
    entries: List[Entry] = []
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
            cursor = conn.cursor()
            cursor.execute("SELECT id, app, title, text, timestamp, embedding FROM entries ORDER BY timestamp DESC")
            results = cursor.fetchall()
            for row in results:
                # Deserialize the embedding blob back into a NumPy array
                embedding = np.frombuffer(row["embedding"], dtype=np.float32) # Assuming float32, adjust if needed
                entries.append(
                    Entry(
                        id=row["id"],
                        app=row["app"],
                        title=row["title"],
                        text=row["text"],
                        timestamp=row["timestamp"],
                        embedding=embedding,
                    )
                )
    except sqlite3.Error as e:
        print(f"Database error while fetching all entries: {e}")
    return entries


def get_timestamps() -> List[int]:
    """
    Retrieves all timestamps from the database, ordered descending.

    Returns:
        List[int]: A list of all timestamps.
                   Returns an empty list if the table is empty or an error occurs.
    """
    timestamps: List[int] = []
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Use the index for potentially faster retrieval
            cursor.execute("SELECT timestamp FROM entries ORDER BY timestamp DESC")
            results = cursor.fetchall()
            timestamps = [result[0] for result in results]
    except sqlite3.Error as e:
        print(f"Database error while fetching timestamps: {e}")
    return timestamps


def insert_entry(
    text: str, timestamp: int, embedding: np.ndarray, app: str, title: str
) -> Optional[int]:
    """
    Inserts a new entry into the database.

    Args:
        text (str): The extracted text content.
        timestamp (int): The Unix timestamp of the screenshot.
        embedding (np.ndarray): The embedding vector for the text.
        app (str): The name of the active application.
        title (str): The title of the active window.

    Returns:
        Optional[int]: The ID of the newly inserted row, or None if insertion fails.
                       Prints an error message to stderr on failure.
    """
    embedding_bytes: bytes = embedding.astype(np.float32).tobytes() # Ensure consistent dtype
    last_row_id: Optional[int] = None
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO entries (text, timestamp, embedding, app, title)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(timestamp) DO NOTHING""", # Avoid duplicates based on timestamp
                (text, timestamp, embedding_bytes, app, title),
            )
            conn.commit()
            if cursor.rowcount > 0: # Check if insert actually happened
                last_row_id = cursor.lastrowid
            # else:
                # Optionally log that a duplicate timestamp was encountered
                # print(f"Skipped inserting entry with duplicate timestamp: {timestamp}")

    except sqlite3.Error as e:
        # More specific error handling can be added (e.g., IntegrityError for UNIQUE constraint)
        print(f"Database error during insertion: {e}")
    return last_row_id


def get_entry_count() -> int:
    """
    Returns the total count of entries in the database.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM entries")
            result = cursor.fetchone()
            return result[0] if result else 0
    except sqlite3.Error as e:
        print(f"Database error while counting entries: {e}")
        return 0


def get_entries_paginated(
    page: int = 1,
    limit: int = 50,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    app_filter: Optional[str] = None
) -> Tuple[List[Entry], int]:
    """
    Get paginated entries with optional filters.

    Args:
        page: Page number (1-indexed)
        limit: Number of entries per page (max 200)
        start_date: Optional Unix timestamp filter start
        end_date: Optional Unix timestamp filter end
        app_filter: Optional app name filter

    Returns:
        Tuple of (entries list, total count matching filters)
    """
    limit = min(limit, 200)  # Cap at 200
    offset = (page - 1) * limit

    entries: List[Entry] = []
    total = 0

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Build WHERE clause
            conditions = []
            params = []

            if start_date is not None:
                conditions.append("timestamp >= ?")
                params.append(start_date)
            if end_date is not None:
                conditions.append("timestamp <= ?")
                params.append(end_date)
            if app_filter:
                conditions.append("app LIKE ?")
                params.append(f"%{app_filter}%")

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM entries{where_clause}", params)
            total = cursor.fetchone()[0]

            # Get paginated entries
            cursor.execute(
                f"SELECT id, app, title, text, timestamp, embedding FROM entries{where_clause} ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                params + [limit, offset]
            )
            results = cursor.fetchall()

            for row in results:
                embedding = np.frombuffer(row["embedding"], dtype=np.float32) if row["embedding"] else None
                entries.append(
                    Entry(
                        id=row["id"],
                        app=row["app"],
                        title=row["title"],
                        text=row["text"],
                        timestamp=row["timestamp"],
                        embedding=embedding,
                    )
                )
    except sqlite3.Error as e:
        print(f"Database error while fetching paginated entries: {e}")

    return entries, total


def get_entry_by_id(entry_id: int) -> Optional[Entry]:
    """
    Get a single entry by ID.

    Args:
        entry_id: The database entry ID

    Returns:
        Entry namedtuple or None if not found
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, app, title, text, timestamp, embedding FROM entries WHERE id = ?",
                (entry_id,)
            )
            row = cursor.fetchone()
            if row:
                embedding = np.frombuffer(row["embedding"], dtype=np.float32) if row["embedding"] else None
                return Entry(
                    id=row["id"],
                    app=row["app"],
                    title=row["title"],
                    text=row["text"],
                    timestamp=row["timestamp"],
                    embedding=embedding,
                )
    except sqlite3.Error as e:
        print(f"Database error while fetching entry by ID: {e}")
    return None


def get_unique_apps() -> List[Tuple[str, int]]:
    """
    Get list of unique apps with their entry counts.

    Returns:
        List of tuples (app_name, count) ordered by count descending
    """
    apps: List[Tuple[str, int]] = []
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT app, COUNT(*) as count FROM entries GROUP BY app ORDER BY count DESC"
            )
            apps = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error while fetching unique apps: {e}")
    return apps


def get_stats() -> Dict[str, Any]:
    """
    Get database and storage statistics.

    Returns:
        Dictionary with stats including total_entries, storage info, date range, top apps
    """
    stats: Dict[str, Any] = {
        "total_entries": 0,
        "storage_used_mb": 0,
        "date_range": {"first_entry": None, "last_entry": None},
        "apps": [],
        "activity_by_hour": []
    }

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Total entries
            cursor.execute("SELECT COUNT(*) FROM entries")
            stats["total_entries"] = cursor.fetchone()[0]

            # Date range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM entries")
            result = cursor.fetchone()
            if result and result[0]:
                stats["date_range"]["first_entry"] = result[0]
                stats["date_range"]["last_entry"] = result[1]

            # Top apps
            cursor.execute(
                "SELECT app, COUNT(*) as count FROM entries GROUP BY app ORDER BY count DESC LIMIT 10"
            )
            stats["apps"] = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]

            # Activity by hour (based on all entries)
            cursor.execute("""
                SELECT CAST(strftime('%H', timestamp, 'unixepoch', 'localtime') AS INTEGER) as hour,
                       COUNT(*) as count
                FROM entries
                GROUP BY hour
                ORDER BY hour
            """)
            stats["activity_by_hour"] = [{"hour": row[0], "count": row[1]} for row in cursor.fetchall()]

    except sqlite3.Error as e:
        print(f"Database error while fetching stats: {e}")

    # Calculate storage used
    try:
        if os.path.exists(screenshots_path):
            total_size = 0
            for filename in os.listdir(screenshots_path):
                filepath = os.path.join(screenshots_path, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
            stats["storage_used_mb"] = round(total_size / (1024 * 1024), 2)
    except OSError as e:
        print(f"Error calculating storage: {e}")

    return stats


def get_entries_by_date(date_str: str) -> List[Entry]:
    """
    Get all entries for a specific date.

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        List of entries for that date
    """
    entries: List[Entry] = []
    try:
        # Parse date and get timestamp range
        date = datetime.strptime(date_str, "%Y-%m-%d")
        start_ts = int(date.timestamp())
        end_ts = start_ts + 86400  # Add 24 hours

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, app, title, text, timestamp, embedding FROM entries WHERE timestamp >= ? AND timestamp < ? ORDER BY timestamp DESC",
                (start_ts, end_ts)
            )
            results = cursor.fetchall()

            for row in results:
                embedding = np.frombuffer(row["embedding"], dtype=np.float32) if row["embedding"] else None
                entries.append(
                    Entry(
                        id=row["id"],
                        app=row["app"],
                        title=row["title"],
                        text=row["text"],
                        timestamp=row["timestamp"],
                        embedding=embedding,
                    )
                )
    except (sqlite3.Error, ValueError) as e:
        print(f"Error fetching entries by date: {e}")

    return entries


def search_entries(query: str, limit: int = 50) -> List[Tuple[Entry, float]]:
    """
    Search entries using embedding similarity.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        List of tuples (Entry, similarity_score) sorted by similarity descending
    """
    from openrecall.nlp import cosine_similarity, get_embedding

    entries = get_all_entries()
    if not entries or not query.strip():
        return []

    query_embedding = get_embedding(query)

    results = []
    for entry in entries:
        if entry.embedding is not None and len(entry.embedding) > 0:
            similarity = cosine_similarity(query_embedding, entry.embedding)
            results.append((entry, float(similarity)))

    # Sort by similarity descending
    results.sort(key=lambda x: x[1], reverse=True)

    return results[:limit]
