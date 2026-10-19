"""CampusPulse AI prototype using Google ADK and Gemini."""
import os
import sys
from pathlib import Path

from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from datetime import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from .tools import get_deadlines, get_weekly_schedule, get_calendar_events

TODAY = datetime.now(ZoneInfo("Asia/Almaty")).date().isoformat()

MCP_SERVER = (
    Path(__file__).resolve().parent.parent
    / "mcp_server.py"
)

mcp_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[str(MCP_SERVER)],
        ),
        timeout=30,
    )
)

root_agent = Agent(
    name="campuspulse_agent",
    model=os.getenv("CAMPUSPULSE_MODEL", "gemini-2.5-flash"),
    description="Student assistant for assignment deadlines and class timetables.",
    instruction=(
        "For student assignments available through MCP, "
        "call get_student_assignments. "
        "When get_calendar_events is used, clearly state that the events "
        "come from the user's real Google Calendar, not sample data. "
        "For real calendar events, call get_calendar_events. "
        "You are CampusPulse AI, a university study assistant. "
        f"Current local date in Astana is {TODAY}. "
        "For requests about deadlines call get_deadlines(reference_date=the current local date, "
        "days_ahead=7 unless the user requests another window). "
        "For requests about weekly classes call get_weekly_schedule. "
        "If a request needs both, call both tools. "
        "Use returned information accurately, show due dates and relevant times. "
        "Do not invent tasks, classes, available study slots, grades, or calendar access. "
        "The data comes from a sample local JSON file, NOT the user's real university or Google Calendar. "
        "Always make this sample-data limitation clear. "
        "If no assignments are returned, say none are found in the specified window. "
        "Keep responses concise; reply in the user's language."
    ),
   tools=[
    get_deadlines,
    get_weekly_schedule,
    get_calendar_events,
    mcp_tools,
],
)
