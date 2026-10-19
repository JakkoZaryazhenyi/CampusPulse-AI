# CampusPulse AI — Step 1 MVP

A read-only Google ADK agent with two tools (`get_deadlines`, `get_weekly_schedule`) backed by **sample JSON**, not real university data.

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `campuspulse_agent/.env`, then replace `YOUR_GEMINI_API_KEY` with a Gemini API key. Never commit this file.

```bash
python -m unittest discover -s tests -v
adk web .
```

Open the local URL ADK prints (often http://127.0.0.1:8000), select `campuspulse_agent`, and try:

> What assignments are due in the next 7 days? Show my weekly class schedule.

To test tool calls without the LLM, run `python -m unittest discover -s tests -v`. In the ADK Web UI, open the event/tool trace to verify function calls.

## Limitations

- Sample assignments are dated October 2026. Dates outside that window will correctly show no upcoming assignments.
- No real Google Calendar integration, no write access, no MCP server yet.
- This first step is local only: **not yet deployed to Vertex AI Agent Engine**.
- Before hackathon submission, add real external tools/MCP and successfully deploy the agent to Agent Engine.

## Security

Never commit API keys. Do not expose personal student records without consent.
