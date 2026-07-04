"""
main.py — FastAPI backend for the Veltix support inbox dashboard.

Run with:
    uvicorn backend.main:app --reload

Then visit:
    http://localhost:8000/docs   ← interactive API explorer (free, auto-generated)
    http://localhost:8000/redoc  ← alternative docs view
"""

import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.database import get_connection, get_all_emails, get_email_by_id, get_stats
from backend.models import EmailListResponse, EmailDetail, StatsResponse, HealthResponse

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Veltix Support Inbox API",
    description="Backend for the Veltix email dashboard — processes and serves support inbox data.",
    version="1.0.0",
)

# CORS middleware — allows your React frontend (running on a different port)
# to make requests to this API. Without this, the browser blocks the requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev port
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
def health():
    """Quick check that the API is alive. Useful for monitoring."""
    return {"status": "ok"}


@app.get("/stats", response_model=StatsResponse)
def stats():
    """
    Aggregate stats for the dashboard summary cards.
    Returns total email count broken down by category, urgency, sentiment, and subscription tier.
    """
    conn = get_connection()
    try:
        return get_stats(conn)
    finally:
        conn.close()


@app.get("/emails", response_model=EmailListResponse)
def list_emails(
    category: str | None = Query(default=None, description="Filter by category"),
    urgency:  str | None = Query(default=None, description="Filter by urgency"),
    sentiment: str | None = Query(default=None, description="Filter by sentiment"),
    limit: int = Query(default=100, le=500, description="Max results to return"),
):
    """
    List emails with optional filters. All filters are optional and combinable.

    Category options : billing, bug_report, feature_request, churn_risk, onboarding, general_support
    Urgency options  : low, medium, high, critical
    Sentiment options: positive, neutral, negative
    """
    conn = get_connection()
    try:
        emails = get_all_emails(conn, category=category, urgency=urgency, sentiment=sentiment, limit=limit)

        # key_topics is stored as a JSON string in SQLite — parse it back to a list
        for email in emails:
            if isinstance(email.get("key_topics"), str):
                email["key_topics"] = json.loads(email["key_topics"])

        return {"count": len(emails), "emails": emails}
    finally:
        conn.close()


@app.get("/emails/{email_id}", response_model=EmailDetail)
def get_email(email_id: str):
    """
    Fetch a single email by ID with full body text and all extracted fields.
    Returns 404 if the email doesn't exist.
    """
    conn = get_connection()
    try:
        email = get_email_by_id(conn, email_id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        if isinstance(email.get("key_topics"), str):
            email["key_topics"] = json.loads(email["key_topics"])

        return email
    finally:
        conn.close()