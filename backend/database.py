"""
database.py — SQLite layer for the Veltix support inbox dashboard.

Two tables:
  raw_emails       — the original email as received, never modified
  processed_emails — AI-extracted structured data, linked by email id

This separation means we can always re-run extraction on the originals
without losing anything. The processed table is essentially disposable
and rebuildable — the raw table is the source of truth.
"""

import sqlite3
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "veltix.db")


def get_connection() -> sqlite3.Connection:
    """
    Open a database connection with row_factory set so every query
    returns rows as dictionaries instead of plain tuples.
    That means you can do row["subject"] instead of row[3].
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS raw_emails (
            id              TEXT PRIMARY KEY,
            sender_name     TEXT NOT NULL,
            sender_email    TEXT NOT NULL,
            sender_company  TEXT NOT NULL,
            subscription_tier TEXT NOT NULL,
            subject         TEXT NOT NULL,
            body            TEXT NOT NULL,
            sent_at         TEXT NOT NULL,
            received_at     TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS processed_emails (
            id                  TEXT PRIMARY KEY,
            email_id            TEXT NOT NULL REFERENCES raw_emails(id),
            category            TEXT NOT NULL,
            sentiment           TEXT NOT NULL,
            urgency             TEXT NOT NULL,
            summary             TEXT NOT NULL,
            action_required     TEXT NOT NULL,
            key_topics          TEXT NOT NULL,   -- stored as JSON array string
            extraction_status   TEXT NOT NULL,
            processed_at        TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_processed_email_id
            ON processed_emails(email_id);

        CREATE INDEX IF NOT EXISTS idx_processed_category
            ON processed_emails(category);

        CREATE INDEX IF NOT EXISTS idx_processed_urgency
            ON processed_emails(urgency);
    """)

    conn.commit()
    conn.close()
    print(f"Database ready → {DB_PATH}")


# ---------------------------------------------------------------------------
# Write operations
# ---------------------------------------------------------------------------

def insert_raw_email(conn: sqlite3.Connection, email: dict) -> None:
    conn.execute("""
        INSERT OR IGNORE INTO raw_emails
            (id, sender_name, sender_email, sender_company,
             subscription_tier, subject, body, sent_at, received_at)
        VALUES
            (:id, :sender_name, :sender_email, :sender_company,
             :subscription_tier, :subject, :body, :sent_at, :received_at)
    """, email)


def insert_processed_email(conn: sqlite3.Connection, email: dict) -> None:
    conn.execute("""
        INSERT OR IGNORE INTO processed_emails
            (id, email_id, category, sentiment, urgency,
             summary, action_required, key_topics,
             extraction_status, processed_at)
        VALUES
            (:id, :email_id, :category, :sentiment, :urgency,
             :summary, :action_required, :key_topics,
             :extraction_status, :processed_at)
    """, email)


# ---------------------------------------------------------------------------
# Read operations (these become your FastAPI endpoints)
# ---------------------------------------------------------------------------

def get_all_emails(
    conn: sqlite3.Connection,
    category: str | None = None,
    urgency: str | None = None,
    sentiment: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """
    Fetch emails joined with their processed data.
    Optional filters for category, urgency, and sentiment.
    """
    query = """
        SELECT
            r.id, r.sender_name, r.sender_email, r.sender_company,
            r.subscription_tier, r.subject, r.sent_at,
            p.category, p.sentiment, p.urgency,
            p.summary, p.action_required, p.key_topics
        FROM raw_emails r
        JOIN processed_emails p ON r.id = p.email_id
        WHERE p.extraction_status = 'success'
    """
    params = []

    if category:
        query += " AND p.category = ?"
        params.append(category)
    if urgency:
        query += " AND p.urgency = ?"
        params.append(urgency)
    if sentiment:
        query += " AND p.sentiment = ?"
        params.append(sentiment)

    query += " ORDER BY r.sent_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_email_by_id(conn: sqlite3.Connection, email_id: str) -> dict | None:
    """Fetch a single email with full body and all extracted fields."""
    row = conn.execute("""
        SELECT
            r.*, p.category, p.sentiment, p.urgency,
            p.summary, p.action_required, p.key_topics,
            p.extraction_status, p.processed_at
        FROM raw_emails r
        JOIN processed_emails p ON r.id = p.email_id
        WHERE r.id = ?
    """, (email_id,)).fetchone()

    return dict(row) if row else None


def get_stats(conn: sqlite3.Connection) -> dict:
    """
    Aggregate stats for the dashboard summary cards.
    Returns counts by category, urgency, sentiment, and tier.
    """
    def fetchall_as_dict(query: str) -> dict:
        rows = conn.execute(query).fetchall()
        return {row[0]: row[1] for row in rows}

    total = conn.execute(
        "SELECT COUNT(*) FROM processed_emails WHERE extraction_status = 'success'"
    ).fetchone()[0]

    return {
        "total_emails": total,
        "by_category": fetchall_as_dict(
            "SELECT category, COUNT(*) FROM processed_emails "
            "WHERE extraction_status='success' GROUP BY category"
        ),
        "by_urgency": fetchall_as_dict(
            "SELECT urgency, COUNT(*) FROM processed_emails "
            "WHERE extraction_status='success' GROUP BY urgency"
        ),
        "by_sentiment": fetchall_as_dict(
            "SELECT sentiment, COUNT(*) FROM processed_emails "
            "WHERE extraction_status='success' GROUP BY sentiment"
        ),
        "by_tier": fetchall_as_dict(
            "SELECT r.subscription_tier, COUNT(*) "
            "FROM raw_emails r JOIN processed_emails p ON r.id = p.email_id "
            "WHERE p.extraction_status='success' GROUP BY r.subscription_tier"
        ),
    }


# ---------------------------------------------------------------------------
# Ingestion — load enriched JSON into the database
# ---------------------------------------------------------------------------

def ingest_enriched_json(path: str) -> None:
    """
    Read emails_enriched.json (output of extractor.py) and load
    every record into raw_emails + processed_emails.
    Skips duplicates safely via INSERT OR IGNORE.
    """
    with open(path) as f:
        emails = json.load(f)

    conn = get_connection()
    inserted = 0
    skipped = 0

    for email in emails:
        insert_raw_email(conn, {
            "id":                email["id"],
            "sender_name":       email["sender_name"],
            "sender_email":      email["sender_email"],
            "sender_company":    email["sender_company"],
            "subscription_tier": email["subscription_tier"],
            "subject":           email["subject"],
            "body":              email["body"],
            "sent_at":           email["sent_at"],
            "received_at":       email["received_at"],
        })

        if email.get("extraction_status") == "success":
            insert_processed_email(conn, {
                "id":               email["id"] + "_proc",
                "email_id":         email["id"],
                "category":         email["ai_category"],
                "sentiment":        email["ai_sentiment"],
                "urgency":          email["ai_urgency"],
                "summary":          email["ai_summary"],
                "action_required":  email["ai_action_required"],
                "key_topics":       json.dumps(email["ai_key_topics"]),
                "extraction_status": "success",
                "processed_at":     datetime.now().isoformat(),
            })
            inserted += 1
        else:
            skipped += 1

    conn.commit()
    conn.close()

    print(f"Ingested {inserted} emails into database.")
    if skipped:
        print(f"Skipped {skipped} failed extractions.")


if __name__ == "__main__":
    enriched_path = os.path.join(BASE_DIR, "data", "emails_enriched.json")
    init_db()
    ingest_enriched_json(enriched_path)

    # Quick sanity check
    conn = get_connection()
    stats = get_stats(conn)
    conn.close()

    print(f"\nDatabase stats:")
    print(f"  Total emails : {stats['total_emails']}")
    print(f"  By category  : {stats['by_category']}")
    print(f"  By urgency   : {stats['by_urgency']}")
    print(f"  By sentiment : {stats['by_sentiment']}")