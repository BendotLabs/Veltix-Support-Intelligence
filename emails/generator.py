"""
Email Generator for Veltix — a fictional B2B SaaS project management tool.
Produces realistic support inbox emails across 6 categories with varied
sentiment, urgency, and writing styles.
"""

import random
import json
import uuid
import os
from datetime import datetime, timedelta
from faker import Faker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

fake = Faker()

# ---------------------------------------------------------------------------
# Company context
# ---------------------------------------------------------------------------

COMPANY_NAME = "Veltix"
PRODUCT_DESC = "B2B project management and team collaboration SaaS"

SUBSCRIPTION_TIERS = ["Starter", "Pro", "Business", "Enterprise"]

# Fictional companies emailing in
SENDER_COMPANIES = [
    "Hartwell & Sons", "Nova Digital", "Cascade Labs", "Ironwood Group",
    "Blueridge Consulting", "Meridian Tech", "Axiom Partners", "Crestline Co",
    "Duskfield Studio", "Pinnacle Works", "Solara Systems", "Trestle Inc",
    "Verdant Analytics", "Cobalt Ventures", "Ember Collective",
]

# ---------------------------------------------------------------------------
# Email templates by category
# ---------------------------------------------------------------------------

BILLING_EMAILS = [
    {
        "subject": "Charged twice this month — need refund",
        "body": (
            "Hi Veltix support,\n\n"
            "I just noticed two charges from you on my card this month — both for ${amount}. "
            "I'm on the {tier} plan and should only be charged once. "
            "This is pretty frustrating, I've been a customer for {months} months without issues. "
            "Can you sort this out and issue a refund for the duplicate? I need this resolved ASAP.\n\n"
            "Thanks,\n{name}"
        ),
        "urgency": "high",
        "sentiment": "negative",
    },
    {
        "subject": "Upgrading to {tier} — a few questions first",
        "body": (
            "Hello,\n\n"
            "We've been on the {current_tier} plan for a while now and we're considering upgrading to {tier}. "
            "Before we do, I wanted to confirm a couple things: does the {tier} plan include SSO? "
            "And can we get a prorated credit for the remainder of our current billing cycle?\n\n"
            "Happy to jump on a call if that's easier.\n\nBest,\n{name}\n{company}"
        ),
        "urgency": "low",
        "sentiment": "positive",
    },
    {
        "subject": "Invoice #{invoice} — payment failed",
        "body": (
            "Hi there,\n\n"
            "We received a notification that our payment for invoice #{invoice} failed. "
            "Our card on file was recently updated — I think that might be the issue. "
            "I've updated the billing details in our account settings. "
            "Could you retry the charge or send us a new payment link?\n\n"
            "We don't want any interruption to our service.\n\nThanks,\n{name}"
        ),
        "urgency": "high",
        "sentiment": "neutral",
    },
    {
        "subject": "Need to cancel our subscription",
        "body": (
            "Hi,\n\n"
            "Unfortunately we need to cancel our {tier} subscription. "
            "Our team has downsized and we just can't justify the cost right now. "
            "It's not a reflection of the product — we've actually really liked using Veltix. "
            "Can you confirm the cancellation and let me know if there's any data export I should do first?\n\n"
            "Thanks for everything,\n{name} at {company}"
        ),
        "urgency": "medium",
        "sentiment": "neutral",
    },
]

BUG_REPORT_EMAILS = [
    {
        "subject": "Bug: file attachments failing on project #{project_id}",
        "body": (
            "Hey support team,\n\n"
            "Running into a consistent issue — every time I try to attach a file larger than ~{size}MB "
            "to a task in project #{project_id}, the upload spins and then fails silently. "
            "No error message, the file just doesn't appear. "
            "Tried on Chrome and Firefox, same result. Started happening after your update on {date}.\n\n"
            "This is blocking a few of my team members. Can you look into it?\n\nBest,\n{name}"
        ),
        "urgency": "high",
        "sentiment": "negative",
    },
    {
        "subject": "Minor UI bug — date picker behaves oddly",
        "body": (
            "Hi,\n\n"
            "Not a blocker but wanted to flag it — the date picker on the task creation modal "
            "sometimes shows the wrong month when you first open it. Clicking away and re-opening "
            "usually fixes it. Using the latest Chrome on Windows 11.\n\n"
            "Keep up the good work otherwise, love the recent updates!\n\n{name}"
        ),
        "urgency": "low",
        "sentiment": "positive",
    },
    {
        "subject": "URGENT: dashboard completely broken — team cannot work",
        "body": (
            "This is urgent. Our entire team has been locked out of the dashboard since {time} this morning. "
            "We're getting a blank white screen after login. We're on the {tier} plan and have {users} users "
            "affected. This is costing us real time and money. "
            "I need someone to respond immediately — if this isn't fixed in the next hour we're going to "
            "have to seriously reconsider our subscription.\n\n{name}, {company}"
        ),
        "urgency": "critical",
        "sentiment": "negative",
    },
    {
        "subject": "Notification emails going to spam",
        "body": (
            "Hi Veltix,\n\n"
            "A few people on my team have noticed that task notification emails are landing in spam. "
            "I checked the email headers and it looks like SPF/DKIM might not be fully configured on "
            "your sending domain. Flagging in case it's useful — happy to share the headers if that helps.\n\n"
            "Cheers,\n{name}"
        ),
        "urgency": "medium",
        "sentiment": "neutral",
    },
]

FEATURE_REQUEST_EMAILS = [
    {
        "subject": "Feature request: recurring tasks",
        "body": (
            "Hi team,\n\n"
            "One thing that's been on my wishlist since we started using Veltix: recurring tasks. "
            "We have a lot of weekly and monthly processes and right now we're manually duplicating tasks "
            "every cycle. Even a simple repeat option (daily / weekly / monthly) would save us a ton of time.\n\n"
            "Any chance this is on the roadmap? Happy to be a beta tester if so.\n\nThanks,\n{name}"
        ),
        "urgency": "low",
        "sentiment": "positive",
    },
    {
        "subject": "Can you add a Slack integration?",
        "body": (
            "Hello,\n\n"
            "We're heavy Slack users and the context switching between Veltix and Slack is a real pain point. "
            "Would love to see a native integration — even just task creation from Slack and "
            "notification delivery to channels would be huge for us. "
            "Is that something you're working on?\n\n{name} @ {company}"
        ),
        "urgency": "medium",
        "sentiment": "neutral",
    },
    {
        "subject": "Time tracking — critical for our workflow",
        "body": (
            "Hi,\n\n"
            "We switched to Veltix from {competitor} mostly because of the UI and pricing, but we "
            "really miss the built-in time tracking. Right now we're using a separate tool which is "
            "clunky. If Veltix added even basic time logging per task, we'd consolidate everything here. "
            "Please pass this along to your product team — I think a lot of agencies would love this.\n\n"
            "Thanks,\n{name}"
        ),
        "urgency": "medium",
        "sentiment": "neutral",
    },
]

CHURN_RISK_EMAILS = [
    {
        "subject": "Considering switching to {competitor}",
        "body": (
            "Hi,\n\n"
            "I'll be honest — we've been evaluating {competitor} lately. "
            "The main thing pulling us away is {pain_point}. "
            "We've been with Veltix for {months} months and generally like the product, "
            "but this has become a real blocker for our team.\n\n"
            "Is there anything on the roadmap that addresses this? "
            "Or is there something we might be missing in the current product?\n\n{name}"
        ),
        "urgency": "high",
        "sentiment": "negative",
    },
    {
        "subject": "What's your cancellation policy?",
        "body": (
            "Hi support,\n\n"
            "Can you walk me through your cancellation policy? "
            "Specifically: what happens to our data, is there a notice period, "
            "and are we locked into the remainder of our annual contract?\n\n"
            "Just exploring our options at the moment.\n\n{name}"
        ),
        "urgency": "high",
        "sentiment": "neutral",
    },
]

ONBOARDING_EMAILS = [
    {
        "subject": "Getting started — a few setup questions",
        "body": (
            "Hi Veltix team,\n\n"
            "We just signed up for the {tier} plan and we're trying to get everyone set up. "
            "A couple of questions:\n\n"
            "1. Is there a bulk invite option for adding team members? We have {users} people to add.\n"
            "2. Can we import tasks from a CSV?\n"
            "3. Is there a getting started guide or video walkthrough you'd recommend?\n\n"
            "Thanks in advance!\n{name} @ {company}"
        ),
        "urgency": "medium",
        "sentiment": "positive",
    },
    {
        "subject": "Trial ending soon — quick question before we commit",
        "body": (
            "Hi,\n\n"
            "Our trial ends in {days} days and we're close to committing to the {tier} plan. "
            "One thing holding us back: does {tier} include custom fields on tasks? "
            "That's a must-have for our workflow.\n\n"
            "If yes, we're ready to upgrade today.\n\n{name}"
        ),
        "urgency": "high",
        "sentiment": "positive",
    },
]

GENERAL_SUPPORT_EMAILS = [
    {
        "subject": "How do I export my project data?",
        "body": (
            "Hi,\n\nQuick question — is there a way to export all tasks and comments from a project? "
            "Ideally as CSV or Excel. I've looked through the settings but can't find it.\n\nThanks,\n{name}"
        ),
        "urgency": "low",
        "sentiment": "neutral",
    },
    {
        "subject": "Permission settings — can't figure out guest access",
        "body": (
            "Hello,\n\n"
            "We're trying to give a client view-only access to one of our projects but I can't "
            "figure out how guest permissions work. Every time I add them they seem to get full edit access. "
            "Can you walk me through the correct setup?\n\nThanks,\n{name} at {company}"
        ),
        "urgency": "medium",
        "sentiment": "neutral",
    },
    {
        "subject": "Love the new {feature} update!",
        "body": (
            "Hey Veltix team,\n\n"
            "Just wanted to say the new {feature} feature is exactly what we needed. "
            "My team has been asking for something like this for months. "
            "Really appreciate you all listening to feedback — keep it up!\n\nBest,\n{name}"
        ),
        "urgency": "low",
        "sentiment": "positive",
    },
]

CATEGORIES = {
    "billing": BILLING_EMAILS,
    "bug_report": BUG_REPORT_EMAILS,
    "feature_request": FEATURE_REQUEST_EMAILS,
    "churn_risk": CHURN_RISK_EMAILS,
    "onboarding": ONBOARDING_EMAILS,
    "general_support": GENERAL_SUPPORT_EMAILS,
}

# Category weights — churn and billing slightly rarer, bugs and support common
CATEGORY_WEIGHTS = [0.18, 0.28, 0.18, 0.10, 0.12, 0.14]

COMPETITORS = ["Asana", "Monday.com", "ClickUp", "Notion", "Linear", "Basecamp"]
PAIN_POINTS = [
    "the lack of time tracking",
    "no native Gantt chart view",
    "the reporting features feel limited",
    "we need better guest/client access controls",
    "the mobile app is too limited for our field team",
]
FEATURES = ["kanban board", "dashboard widgets", "task dependencies", "dark mode", "bulk editing"]

# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def fill_template(template: str, tier: str, company: str, name: str) -> str:
    """Fill placeholders in an email template with realistic fake values."""
    replacements = {
        "{name}": name,
        "{company}": company,
        "{tier}": tier,
        "{current_tier}": random.choice([t for t in SUBSCRIPTION_TIERS if t != tier]),
        "{amount}": str(random.choice([49, 79, 99, 149, 299])),
        "{months}": str(random.randint(2, 24)),
        "{invoice}": str(random.randint(10000, 99999)),
        "{project_id}": str(random.randint(100, 9999)),
        "{size}": str(random.choice([10, 25, 50, 100])),
        "{date}": (datetime.now() - timedelta(days=random.randint(1, 7))).strftime("%B %d"),
        "{time}": f"{random.randint(6, 11)}:{random.choice(['00','15','30','45'])} AM",
        "{users}": str(random.randint(5, 80)),
        "{days}": str(random.randint(2, 7)),
        "{competitor}": random.choice(COMPETITORS),
        "{pain_point}": random.choice(PAIN_POINTS),
        "{feature}": random.choice(FEATURES),
    }
    result = template
    for key, value in replacements.items():
        result = result.replace(key, value)
    return result


def generate_email(
    sent_at: datetime | None = None,
) -> dict:
    """Generate a single realistic fake support email."""
    category = random.choices(list(CATEGORIES.keys()), weights=CATEGORY_WEIGHTS, k=1)[0]
    template = random.choice(CATEGORIES[category])

    tier = random.choice(SUBSCRIPTION_TIERS)
    company = random.choice(SENDER_COMPANIES)
    name = fake.name()
    sender_email = f"{name.split()[0].lower()}.{name.split()[-1].lower()}@{company.lower().replace(' ', '').replace('&', 'and')}.com"

    subject = fill_template(template["subject"], tier, company, name)
    body = fill_template(template["body"], tier, company, name)

    if sent_at is None:
        # Random time in the last 30 days
        sent_at = datetime.now() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

    return {
        "id": str(uuid.uuid4()),
        "sender_name": name,
        "sender_email": sender_email,
        "sender_company": company,
        "subscription_tier": tier,
        "subject": subject,
        "body": body,
        "category_hint": category,        # raw label — AI will re-derive this
        "urgency_hint": template["urgency"],
        "sentiment_hint": template["sentiment"],
        "sent_at": sent_at.isoformat(),
        "received_at": datetime.now().isoformat(),
    }


def generate_batch(count: int = 50, output_path: str = "data/emails.json") -> list[dict]:
    """Generate a batch of emails and save to JSON."""
    emails = [generate_email() for _ in range(count)]
    emails.sort(key=lambda e: e["sent_at"])

    with open(output_path, "w") as f:
        json.dump(emails, f, indent=2)

    print(f"Generated {count} emails → {output_path}")
    print("\nCategory breakdown:")
    from collections import Counter
    counts = Counter(e["category_hint"] for e in emails)
    for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {cat:<20} {n}")

    return emails


if __name__ == "__main__":
    output = os.path.join(BASE_DIR, "data", "emails.json")
    generate_batch(count=50, output_path=output)