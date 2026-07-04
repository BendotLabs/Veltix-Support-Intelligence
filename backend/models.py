"""
models.py — Pydantic response models for the Veltix support inbox API.

These define the exact shape of data that leaves our API.
Benefits:
  - FastAPI validates every response against these automatically
  - /docs shows the full schema for every endpoint
  - Acts as a contract between the backend and the React frontend
  - Catches bugs where database queries return unexpected shapes
"""

from pydantic import BaseModel
from typing import Literal


# ---------------------------------------------------------------------------
# Enums as Literal types
# Restricts fields to only valid values — if the DB returns something
# unexpected, Pydantic catches it immediately instead of silently
# passing bad data to the frontend.
# ---------------------------------------------------------------------------

Category  = Literal["billing", "bug_report", "feature_request", "churn_risk", "onboarding", "general_support"]
Urgency   = Literal["low", "medium", "high", "critical"]
Sentiment = Literal["positive", "neutral", "negative"]
Tier      = Literal["Starter", "Pro", "Business", "Enterprise"]


# ---------------------------------------------------------------------------
# Email models
# ---------------------------------------------------------------------------

class EmailSummary(BaseModel):
    """
    Lightweight email shape for list views.
    Excludes the full body — we don't need to send that for every row
    in a table of 50+ emails.
    """
    id:               str
    sender_name:      str
    sender_email:     str
    sender_company:   str
    subscription_tier: Tier
    subject:          str
    sent_at:          str
    category:         Category
    sentiment:        Sentiment
    urgency:          Urgency
    summary:          str
    action_required:  str
    key_topics:       list[str]


class EmailDetail(EmailSummary):
    """
    Full email shape for the detail view.
    Extends EmailSummary and adds the body — only fetched when a user
    clicks into a specific email.
    """
    body:           str
    received_at:    str
    processed_at:   str | None = None


# ---------------------------------------------------------------------------
# Response wrapper models
# ---------------------------------------------------------------------------

class EmailListResponse(BaseModel):
    """Wraps the emails list with a count — useful for pagination later."""
    count:  int
    emails: list[EmailSummary]


class StatsResponse(BaseModel):
    """Aggregate stats for the dashboard summary cards."""
    total_emails: int
    by_category:  dict[str, int]
    by_urgency:   dict[str, int]
    by_sentiment: dict[str, int]
    by_tier:      dict[str, int]


class HealthResponse(BaseModel):
    status: str