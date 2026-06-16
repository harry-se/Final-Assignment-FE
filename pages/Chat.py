from datetime import datetime
import streamlit as st
import time
import json
import pandas as pd

from services.chat_service import save_session_to_db

st.set_page_config(page_title="Hệ thống AI Quản lý", layout="centered")

st.title("AI Agent Chat with Charts 📊")

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render History chat + chart(if any)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart_data" in msg:
            st.bar_chart(msg["chart_data"]) # Vẽ lại biểu đồ từ lịch sử

# --- GIẢ LẬP BACKEND TRẢ VỀ CẢ TRẠNG THÁI, TEXT VÀ CHART ---
def mock_backend_with_chart():
    # 1. Trả về status
    yield json.dumps({"type": "status", "content": "Đang truy vấn dữ liệu doanh thu..."})
    time.sleep(1)
    
    # 2. Trả về text giải thích trước
    words = "Dưới đây là biểu đồ doanh thu 3 tháng đầu năm 2026 của công ty:"
    for word in words.split():
        yield json.dumps({"type": "token", "content": word + " "})
        time.sleep(0.05)
        
    # 3. Gửi MỘT CHUNK duy nhất chứa toàn bộ dữ liệu biểu đồ
    chart_payload = {
        "type": "chart",
        "content": {
            "Tháng": ["Tháng 1", "Tháng 2", "Tháng 3"],
            "Doanh Thu ($)": [12000, 15000, 18000]
        }
    }
    yield json.dumps(chart_payload)
    time.sleep(0.5)

    # 4. Trả về text nhận xét sau biểu đồ
    more_words = "Nhìn chung doanh thu tăng trưởng đều qua các tháng."
    for word in more_words.split():
        yield json.dumps({"type": "token", "content": word + " "})
        time.sleep(0.05)


# --- LUỒNG XỬ LÝ CHAT TRÊN STREAMLIT ---
if prompt := st.chat_input("Hỏi về doanh thu..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        status = st.status("Đang xử lý...", expanded=True)
        
        # Biến tạm để hứng dữ liệu biểu đồ nếu có trong luồng stream
        detected_chart_data = {"data":None}
        
        def stream_handler():
            for chunk in mock_backend_with_chart():
                data = json.loads(chunk)
                
                if data["type"] == "status":
                    status.update(label=data["content"])
                elif data["type"] == "token":
                    yield data["content"]
                elif data["type"] == "chart":
                    # Lưu lại dữ liệu biểu đồ, không yield cho st.write_stream
                    detected_chart_data["data"] = data["content"]

        # Gọi write_stream để gõ chữ, khi gặp chart nó sẽ bỏ qua và chạy tiếp text phía sau
        final_response = st.write_stream(stream_handler())
        status.update(label="Đã xử lý xong!", state="complete", expanded=False)
        
        # NẾU CÓ BIỂU ĐỒ: Tiến hành vẽ ra giao diện ngay dưới dòng chữ
        if detected_chart_data["data"]:
            # Chuyển dữ liệu JSON thành DataFrame của Pandas để Streamlit dễ vẽ
            df = pd.DataFrame(detected_chart_data["data"])
            df = df.set_index("Tháng") # Chọn cột làm trục X
            
            # Vẽ biểu đồ cột (Bar Chart)
            st.bar_chart(df)
            
            # Lưu vào session_state bao gồm cả text và dữ liệu biểu đồ để không bị mất khi rerun
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_response, 
                "chart_data": df
            })
        else:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_response
            })

        save_session_to_db(st.session_state.current_session_id, st.session_state.messages)

if st.button("New Chat ➕"):
    st.session_state.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.messages = []
    st.rerun()