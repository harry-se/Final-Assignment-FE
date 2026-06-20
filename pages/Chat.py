from datetime import datetime
import streamlit as st
import time
import json

from components import chart_renderer
from services import chat_service

# st.set_page_config(page_title="Hệ thống AI Quản lý", layout="centered")

st.markdown("""
<style>
div.stButton {
    position: fixed;
    top: 10%;
    right: 40px;
    width: fit-content;
}
</style>
""", unsafe_allow_html=True)

if st.button("➕ New Chat"):
    st.session_state.current_session_id = chat_service.create_conversation()
    st.session_state.messages = []
    st.rerun()

st.title("Call Center Analytics Agent", text_alignment="center")

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = chat_service.create_conversation()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render History chat + chart(if any)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["message"])
        if "chart_data" in msg:
            chart_type = msg.get("chart_type", "bar")
            chart_renderer.render_dynamic_chart(msg["chart_data"], chart_type)


# == CHAT PROCESSING STREAMLIT ==
if prompt := st.chat_input("Ask me something..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "message": prompt})

    with st.chat_message("assistant"):
        status = st.status("Processing...", expanded=True)
        
        detected_chart_data = {"data": None, "chart_type": "bar"}

        final_response = st.write_stream(
            chat_service.stream_handler(
                status,
                prompt,
                st.session_state.current_session_id,
                detected_chart_data,
            )
        )
        if detected_chart_data.get("conversation_id"):
            st.session_state.current_session_id = detected_chart_data["conversation_id"]
        status.update(label="Process completed!", state="complete", expanded=True)
        
        if detected_chart_data["data"]:
            chart_renderer.render_dynamic_chart(detected_chart_data["data"], detected_chart_data["chart_type"])
            
            # Store into session_state
            st.session_state.messages.append({
                "role": "assistant", 
                "message": final_response, 
                "chart_data": detected_chart_data["data"],
                "chart_type": detected_chart_data["chart_type"]
            })
        else:
            st.session_state.messages.append({
                "role": "assistant", 
                "message": final_response
            })

        chat_service.save_session_to_local_file(st.session_state.current_session_id, st.session_state.messages)
