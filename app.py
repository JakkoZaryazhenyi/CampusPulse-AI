import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(
    Path(__file__).resolve().parent
    / "campuspulse_agent"
    / ".env"
)
import streamlit as st
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from campuspulse_agent.agent import root_agent
from datetime import datetime
from zoneinfo import ZoneInfo

from campuspulse_agent.tools import (
    get_deadlines,
    get_weekly_schedule,
    get_calendar_events,
)

st.set_page_config(
    page_title="CampusPulse AI",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 CampusPulse AI")
st.caption("Your Intelligent University Assistant")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Choose a page",
    ["Dashboard", "AI Chat", "Calendar", "Deadlines"],
)

if page == "Dashboard":
    st.header("📊 Student Dashboard")
    st.success("Welcome to CampusPulse AI!")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("AI Tools", "3")

    with col2:
        st.metric("Calendar", "Connected")

    with col3:
        st.metric("Platform", "Google ADK")

    st.info("Your AI-powered academic assistant is ready.")

elif page == "AI Chat":
    st.header("🤖 CampusPulse AI Chat")
    st.caption("Powered by Gemini + Google ADK")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input("Ask CampusPulse AI anything...")

    if user_input:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("CampusPulse AI is thinking..."):

                async def ask_agent():
                    runner = InMemoryRunner(
                        agent=root_agent,
                        app_name="campuspulse_streamlit"
                    )

                    session = await runner.session_service.create_session(
                        app_name="campuspulse_streamlit",
                        user_id="student"
                    )

                    content = types.Content(
                        role="user",
                        parts=[types.Part(text=user_input)]
                    )

                    response_text = ""

                    async for event in runner.run_async(
                        user_id="student",
                        session_id=session.id,
                        new_message=content
                    ):
                        if event.is_final_response() and event.content:
                            response_text = "".join(
                                part.text
                                for part in event.content.parts
                                if part.text
                            )

                    return response_text

                try:
                    answer = asyncio.run(ask_agent())

                    if not answer:
                        answer = "No response received from AI."

                    st.write(answer)

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:
                    st.error(f"AI Error: {type(e).__name__}: {e}")

elif page == "Calendar":
    st.header("📅 Google Calendar")

    if st.button("Load Calendar Events"):
        result = get_calendar_events(days_ahead=7)

        if "error" in result:
            st.error(result["error"])
        elif result["events"]:
            for event in result["events"]:
                st.subheader(event["title"])
                st.write("Start:", event["start"])
                st.write("End:", event["end"])
                st.divider()
        else:
            st.info("No upcoming events found.")

elif page == "Deadlines":
    st.header("📚 Upcoming Assignments")

    today = datetime.now(ZoneInfo("Asia/Almaty")).date()

    result = get_deadlines(
        reference_date=today.isoformat(),
        days_ahead=7,
    )

    if result["assignments"]:
        for assignment in result["assignments"]:
            st.subheader(assignment["title"])
            st.write("Course:", assignment["course"])
            st.write("Due date:", assignment["due_date"])
            st.divider()
    else:
        st.info("No upcoming assignments.")