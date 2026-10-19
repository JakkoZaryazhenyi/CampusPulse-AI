from pathlib import Path
from datetime import datetime, timedelta, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

FOLDER = Path(__file__).resolve().parent
CREDENTIALS_FILE = FOLDER / "credentials.json"
TOKEN_FILE = FOLDER / "token.json"

creds = None

if TOKEN_FILE.exists():
    creds = Credentials.from_authorized_user_file(
        str(TOKEN_FILE), SCOPES
    )

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), SCOPES
        )
        creds = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

service = build("calendar", "v3", credentials=creds)

now = datetime.now(timezone.utc)
end = now + timedelta(days=7)

events = service.events().list(
    calendarId="primary",
    timeMin=now.isoformat(),
    timeMax=end.isoformat(),
    singleEvents=True,
    orderBy="startTime",
    maxResults=20,
).execute()

items = events.get("items", [])

print("\n=== YOUR GOOGLE CALENDAR EVENTS ===")

if not items:
    print("No upcoming events found.")
else:
    for event in items:
        start = event["start"].get(
            "dateTime", event["start"].get("date")
        )
        print(f"{start} | {event.get('summary', 'Untitled')}")