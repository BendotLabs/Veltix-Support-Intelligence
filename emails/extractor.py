"""
Extraction service — sends raw emails to Groq and returns structured data.

For each email we extract:
  - category        : what kind of email this is
  - sentiment       : overall tone
  - urgency         : how time-sensitive it is
  - summary         : one sentence describing the email
  - action_required : what the support team should do
  - key_topics      : short tags for dashboard filtering
"""

import json
import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# ---------------------------------------------------------------------------
# The extraction prompt — this is the core of the service
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a support inbox classifier for Veltix, a B2B SaaS project management tool.

Your job is to analyze incoming customer emails and extract structured data.
You must respond with ONLY valid JSON — no explanation, no markdown, no code fences.

Return exactly this structure:
{
  "category": "<one of: billing, bug_report, feature_request, churn_risk, onboarding, general_support>",
  "sentiment": "<one of: positive, neutral, negative>",
  "urgency": "<one of: low, medium, high, critical>",
  "summary": "<one sentence, max 20 words, describing what the customer wants>",
  "action_required": "<one sentence describing what the support team should do>",
  "key_topics": ["<tag1>", "<tag2>", "<tag3>"]
}

Urgency guide:
  critical — service is down, team cannot work, threatening to leave immediately
  high     — billing error, blocked workflow, needs same-day response
  medium   — question or issue that needs a response within 1-2 days
  low      — general feedback, minor bugs, non-urgent questions

Key topics should be 1-3 word tags relevant to the email content.
Examples: "refund", "SSO", "file upload", "cancellation", "time tracking", "guest access"
"""

def extract(email: dict) -> dict:
    """
    Send a single raw email to Groq and return extracted structured data.
    Raises ValueError if the model returns unparseable output.
    """
    user_message = f"Subject: {email['subject']}\n\n{email['body']}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,   # low temp = more consistent, predictable output
        max_tokens=300,
    )

    raw = response.choices[0].message.content.strip()

    try:
        extracted = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"Model returned non-JSON output:\n{raw}")

    # Validate all expected fields are present
    required_fields = {"category", "sentiment", "urgency", "summary", "action_required", "key_topics"}
    missing = required_fields - extracted.keys()
    if missing:
        raise ValueError(f"Model response missing fields: {missing}\nGot: {extracted}")

    return extracted


def process_batch(
    input_path: str,
    output_path: str,
    delay: float = 0.3,
) -> list[dict]:
    """
    Run the full emails.json through extraction and write enriched results.

    Each output record = original email fields + AI-extracted fields.
    We also keep the generator's hint labels for comparison on the dashboard.

    delay: seconds to wait between Groq calls (avoids rate limit on free tier)
    """
    with open(input_path) as f:
        emails = json.load(f)

    results = []
    errors = []

    print(f"Processing {len(emails)} emails with {MODEL}...\n")

    for i, email in enumerate(emails):
        print(f"  [{i+1:02d}/{len(emails)}] {email['subject'][:55]:<55}", end=" ", flush=True)

        try:
            extracted = extract(email)

            # Merge original email + AI extraction into one record
            record = {
                **email,
                "ai_category": extracted["category"],
                "ai_sentiment": extracted["sentiment"],
                "ai_urgency": extracted["urgency"],
                "ai_summary": extracted["summary"],
                "ai_action_required": extracted["action_required"],
                "ai_key_topics": extracted["key_topics"],
                "extraction_status": "success",
            }
            results.append(record)
            print(f"✓  [{extracted['urgency']:<8}] {extracted['category']}")

        except Exception as e:
            print(f"✗  ERROR: {e}")
            errors.append({"email_id": email["id"], "error": str(e)})
            # Still include the email, just mark it as failed
            results.append({**email, "extraction_status": "failed"})

        time.sleep(delay)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'─'*60}")
    print(f"Done. {len(results) - len(errors)}/{len(emails)} succeeded.")
    if errors:
        print(f"  {len(errors)} failed — check extraction_status field in output.")
    print(f"Output → {output_path}")

    return results


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    process_batch(
        input_path=os.path.join(base, "data", "emails.json"),
        output_path=os.path.join(base, "data", "emails_enriched.json"),
    )