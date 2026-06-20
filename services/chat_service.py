import json
import os
import re

from dotenv import load_dotenv
import requests

# from pages.Chat import mock_backend_with_chart

MOCK_DATA_FILE = "mock_data.json"
HISTORY_FILE = "log_history.json"

load_dotenv()
backend_url = os.getenv("BACKEND_URL","")
print(f"Loaded BACKEND_URL: {backend_url}")


TEXT_BLOCK_REPR_PATTERN = re.compile(
    r"^\[?TextBlock\(type='text', text='(?P<text>.*)', id='[^']+'\)\]?$",
    re.DOTALL,
)


def clean_answer_text(answer):
    if not isinstance(answer, str):
        return answer
    match = TEXT_BLOCK_REPR_PATTERN.match(answer.strip())
    if match:
        answer = match.group("text")
    return (
        answer.replace("\\r\\n", "\n")
        .replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace("\\'", "'")
        .replace('\\"', '"')
    )


def create_conversation():
    try:
        response = requests.post(
            f"{backend_url}/conversations",
            timeout=20
        )
        response.raise_for_status()
        return response.json()["conversation_id"]

    except requests.exceptions.RequestException as ex:
        print(f"Create conversation failed: {ex}")
        return None

def get_all_sessions_from_local_file():
    """Get all chat sessions from local file"""
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {}

def send_prompt(user_message, conversation_id):
    """
    Fetch response from backend API with streaming support
    
    Args:
        user_message: The user's input message
        
    Yields:
        JSON strings containing response chunks
    """
    try:
        
        #  result = requests.post(
        #     f"{backend_url}/chat",
        #     json={"message": user_message, "description": conversation_id},
        #     stream=False
        # )

        payload = {"message": user_message}
        if conversation_id:
            payload["conversation_id"] = conversation_id

        # Send POST request to backend API
        result = requests.post(
            f"{backend_url}/chat/stream",
            json=payload,
            stream=True,
            timeout=120
        )
        result.raise_for_status()
        
        # Stream the response line by line
        for line in result.iter_lines():
            if line:
                try:
                    yield line.decode('utf-8') if isinstance(line, bytes) else line
                except json.JSONDecodeError:
                    continue
    except requests.exceptions.RequestException as e:
        # Fallback: Return error status if backend is unavailable
        yield json.dumps({"type": "status", "message": f"Error connecting to backend: {str(e)}"})
        # Return mock data for demonstration if backend fails
        yield json.dumps({"type": "result", "message": "Backend is currently unavailable. Using demo data: "})
        # yield from mock_backend_with_chart()

def stream_handler(status, prompt, conversation_id, detected_chart_data):
    # Use actual backend API response instead of mock data
    rendered_steps = set()
    rendered_answers = set()
    last_status_message = None

    for chunk in send_prompt(prompt, conversation_id):
        chunk = chunk.strip()

        if not chunk:
            continue

        if chunk.startswith("data: "):
            chunk = chunk[6:]

        try:
            data = json.loads(chunk)
            print(chunk)
            print(data)
        except json.JSONDecodeError:
            print("INVALID JSON:", repr(chunk))
            continue
        
        event_type = data.get("type")
        if data.get("conversation_id"):
            detected_chart_data["conversation_id"] = data["conversation_id"]

        if event_type == "metadata":
            continue
        if event_type == "status":
            status_message = data.get("message", "")
            if status_message and status_message != last_status_message:
                status.update(label=status_message)
                last_status_message = status_message
        elif event_type == "result":
            # Show reasoning steps in status before completing
            reasoning_steps = data.get("reasoning_steps", [])
            if reasoning_steps:
                unique_steps = []
                for step in reasoning_steps:
                    if step not in rendered_steps and step not in unique_steps:
                        unique_steps.append(step)
                if unique_steps:
                    status.update(
                        label=f"Completed — {len(rendered_steps) + len(unique_steps)} steps"
                    )
                for step in reasoning_steps:
                    if step in rendered_steps:
                        continue
                    rendered_steps.add(step)

                    if "error" in step.lower():
                        status.markdown(f"❌ `{step}`")
                    elif "Route intent" in step:
                        status.markdown(f"🧭 `{step}`")
                    elif "retrieve_knowledge" in step:
                        status.markdown(f"📚 `{step}`")
                    elif "execute_sql" in step:
                        status.markdown(f"🗄️ `{step}`")
                    elif "ReAct loop" in step or "llm_calls" in step:
                        status.markdown(f"🤖 `{step}`")
                    else:
                        status.markdown(f"▸ `{step}`")

            # Extract visualization data if present
            visualization = data.get("visualization")
            if visualization:
                # Map BE visualization types to FE chart types
                viz_type_map = {
                    "bar_chart": "bar",
                    "line_chart": "line",
                    "pie_chart": "bar",  # streamlit doesn't have native pie, use bar
                    "table": "table",
                }
                chart_type = viz_type_map.get(visualization.get("type", ""), "bar")
                detected_chart_data["data"] = visualization.get("data")
                detected_chart_data["chart_type"] = chart_type

            # Handle both "answer" and "message" keys
            answer = clean_answer_text(data.get("answer") or data.get("message", ""))
            if answer and answer not in rendered_answers:
                rendered_answers.add(answer)
                yield answer
        elif event_type == "chart":
            detected_chart_data["data"] = data.get("message", data.get("data"))
            detected_chart_data["chart_type"] = data.get("chart_type", "bar")



# mock data functions only
def mock_backend_with_chart():
    """
    Mock backend response generator that reads from mock_data.json
    Replace this with actual backend calls in production
    """
    mock_data = load_mock_data()
    
    if "data" in mock_data and isinstance(mock_data["data"], list):
        for item in mock_data["data"]:
            yield json.dumps(item)
            # Add small delay to simulate streaming
            # time.sleep(0.1)
    else:
        # Fallback if mock_data.json is not properly formatted
        yield json.dumps({"type": "status", "message": "No mock data available"})
        yield json.dumps({"type": "token", "message": "Please configure mock_data.json file"})

def load_mock_data():
    """Load mock data from JSON file"""
    if not os.path.exists(MOCK_DATA_FILE):
        return {}
    with open(MOCK_DATA_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {}

def save_session_to_local_file(session_id, messages):
    """Store current chat session into file"""
    data = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try: data = json.load(f)
            except: pass
            
    data[session_id] = messages
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
