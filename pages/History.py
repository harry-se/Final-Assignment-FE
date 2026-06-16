# pages/History.py
import streamlit as st
from services.chat_service import get_all_sessions_from_db

st.title("Lịch sử trò chuyện ⏳")

# Lấy toàn bộ dữ liệu lịch sử từ database/file
all_sessions = get_all_sessions_from_db()

if not all_sessions:
    st.info("Bạn chưa có phiên thảo luận nào trước đây.")
else:
    # Tạo danh sách các Session ID để người dùng chọn
    session_list = list(all_sessions.keys())
    
    # Format lại tên hiển thị cho đẹp mắt (ví dụ: phiên ngày... lúc...)
    selected_session = st.selectbox(
        "Chọn phiên chat muốn xem lại:", 
        options=session_list,
        format_func=lambda x: f"Cuộc trò chuyện lúc {x.replace('_', ' ')}"
    )
    
    st.divider()
    
    # Lấy nội dung tin nhắn của phiên chat được chọn
    saved_messages = all_sessions[selected_session]
    
    # Hiển thị lại toàn bộ dưới dạng giao diện Chat nhưng ở chế độ Read-only
    for msg in saved_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])