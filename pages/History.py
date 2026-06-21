from datetime import datetime

import pandas as pd
import streamlit as st
from services.history_service import get_conversation, get_conversation_by_id, delete_conversation

# --- MOCK DATA LOADING (Commented out - now using backend API) ---
# from services.chat_service import get_all_sessions_from_local_file
# all_sessions = get_all_sessions_from_local_file()

st.title("History of Chat Sessions")


def normalize_conversation(conversation):
    if isinstance(conversation, str):
        return {
            "conversation_id": conversation,
            "title": None,
            "message_count": None,
            "updated_at": None,
        }
    return conversation


def format_datetime(value):
    if not value:
        return "Unknown time"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime(
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return value


def conversation_label(conversation):
    title = conversation.get("title") or "Untitled conversation"
    message_count = conversation.get("message_count")
    updated_at = format_datetime(conversation.get("updated_at"))
    if message_count is None:
        return f"{title} · {updated_at}"
    return f"{title} · {message_count} messages · {updated_at}"

# Function to render charts dynamically based on chart type
def render_dynamic_chart(chart_data, chart_type="bar"):
    """
    Render chart(s) dynamically based on the chart type
    
    Args:
        chart_data: Dictionary or list of dictionaries containing chart data
        chart_type: Type of chart (bar, line, area, scatter)
    """
    # Handle multiple charts (list of chart data)
    if isinstance(chart_data, list):
        for single_chart in chart_data:
            render_single_chart(single_chart, chart_type)
    else:
        render_single_chart(chart_data, chart_type)

def render_single_chart(chart_data, chart_type="bar"):
    """
    Render a single chart from dictionary data
    
    Args:
        chart_data: Dictionary containing chart data
        chart_type: Type of chart (bar, line, area, scatter)
    """
    df = pd.DataFrame(chart_data)
    
    if len(df.columns) > 1:
        first_col = df.columns[0]
        if df[first_col].dtype == 'object' or df[first_col].dtype == 'string':
            df = df.set_index(first_col)
    
    if chart_type == "bar":
        st.bar_chart(df)
    elif chart_type == "line":
        st.line_chart(df)
    elif chart_type == "area":
        st.area_chart(df)
    elif chart_type == "scatter":
        st.scatter_chart(df)
    else:
        st.bar_chart(df)


# --- FETCH CONVERSATION LIST FROM BACKEND ---
all_sessions = [normalize_conversation(item) for item in get_conversation()]

if not all_sessions:
    st.info("You did not have any previous chat sessions.")
else:
    selected_session = st.selectbox(
        "Chọn phiên chat muốn xem lại:",
        options=all_sessions,
        format_func=conversation_label,
    )
    selected_session_id = selected_session["conversation_id"]
    
    # Add delete button with confirmation
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Continue in Chat", key=f"resume_{selected_session_id}"):
            st.session_state.resume_conversation_id = selected_session_id
            st.switch_page("pages/Chat.py")

    with col2:
        if st.button("🗑️ Delete", key=f"delete_{selected_session_id}"):
            if delete_conversation(selected_session_id):
                if st.session_state.get("current_session_id") == selected_session_id:
                    st.session_state.pop("current_session_id", None)
                    st.session_state.pop("messages", None)
                    st.session_state.pop("loaded_session_id", None)
                    st.session_state.pop("resume_conversation_id", None)
                st.success("Conversation deleted successfully!")
                st.rerun()
            else:
                st.error("Failed to delete conversation")
    
    st.divider()
    
    # --- FETCH CONVERSATION MESSAGES FROM BACKEND ---
    conversation_data = get_conversation_by_id(selected_session_id)
    
    if conversation_data is None:
        st.error("Failed to load conversation messages")
    else:
        # Extract messages from backend response
        messages = conversation_data.get("messages", [])
        
        if not messages:
            st.info("No messages in this conversation")
        else:
            # Display messages (Read-only)
            for msg in messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    
                    # Handle chart data if available
                    if "chart_data" in msg:
                        chart_data = msg["chart_data"]
                        
                        if isinstance(chart_data, dict) and "data" in chart_data:
                            chart_data = chart_data["data"]
                        
                        chart_type = msg.get("chart_type", "bar")
                        
                        render_dynamic_chart(chart_data, chart_type)
