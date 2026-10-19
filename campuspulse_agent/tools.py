"""Read-only sample academic tools; replace with real connectors in phase 2."""
import json
from datetime import date
from pathlib import Path

_DATA_FILE = Path(__file__).with_name("data.json")


def _data() -> dict:
    with _DATA_FILE.open(encoding="utf-8") as handle:
        return json.load(handle)


def get_deadlines(reference_date: str, days_ahead: int = 7) -> dict:
    """Return pending assignments due in the given window.

    Args:
        reference_date: Today's date in YYYY-MM-DD format, supplied by user or context.
        days_ahead: Number of days to look ahead, between 0 and 60.

    Returns:
        Dictionary containing the date window, assignments and errors if any.
    """
    try:
        start = date.fromisoformat(reference_date)
    except ValueError:
        return {"error": "reference_date must be a valid YYYY-MM-DD date"}
    if not 0 <= days_ahead <= 60:
        return {"error": "days_ahead must be between 0 and 60"}
    from datetime import timedelta
    end = start + timedelta(days=days_ahead)
    results = []
    for item in _data()["assignments"]:
        if item["status"] != "pending":
            continue
        try:
            due = date.fromisoformat(item["due_date"])
        except ValueError:
            continue
        if start <= due <= end:
            results.append({**item, "days_remaining": (due - start).days})
    results.sort(key=lambda a: a["due_date"])
    return {"source": "sample_local_json", "reference_date": start.isoformat(),
            "through_date": end.isoformat(), "assignments": results}


def get_weekly_schedule() -> dict:
    """Return the student's weekly class schedule from sample local data.

    Returns:
        Dictionary with source label and scheduled courses.
    """
    return {"source": "sample_local_json", "timezone": "Asia/Almaty",
            "classes": _data()["courses"]}
def get_calendar_events(days_ahead: int = 7) -> dict:
    """Get upcoming real Google Calendar events.

    Args:
        days_ahead: Number of days to look ahead, between 1 and 30.

    Returns:
        Dictionary containing real calendar events or an error.
    """
    from datetime import datetime, timedelta, timezone
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    if not 1 <= days_ahead <= 30:
        return {"error": "days_ahead must be between 1 and 30"}

    folder = Path(__file__).resolve().parent
    token_file = folder / "token.json"

    if not token_file.exists():
        return {"error": "Google Calendar is not connected. Run calendar_test.py first."}

    scopes = ["https://www.googleapis.com/auth/calendar.readonly"]

    try:
        creds = Credentials.from_authorized_user_file(
            str(token_file), scopes
        )

        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                token_file.write_text(
                    creds.to_json(), encoding="utf-8"
                )
            else:
                return {"error": "Google Calendar authorization expired. Reconnect your account."}

        service = build("calendar", "v3", credentials=creds)

        now = datetime.now(timezone.utc)
        end = now + timedelta(days=days_ahead)

        response = service.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
            maxResults=50,
        ).execute()

        events = []
        for event in response.get("items", []):
            events.append({
                "title": event.get("summary", "Untitled"),
                "start": event["start"].get(
                    "dateTime", event["start"].get("date")
                ),
                "end": event["end"].get(
                    "dateTime", event["end"].get("date")
                ),
            })

        return {
            "source": "google_calendar",
            "days_ahead": days_ahead,
            "events": events,
        }

    except Exception as exc:
        return {
            "error": f"Google Calendar request failed: {type(exc).__name__}"
        }