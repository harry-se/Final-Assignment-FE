## Data Flow & API Specification

The system utilizes **Server-Sent Events (SSE)** or **JSON Lines** streaming mechanisms to facilitate real-time data transfer from the Backend to the Frontend (Streamlit). This approach allows the UI to display the AI's step-by-step reasoning process (Agentic Workflow) before rendering the final response.

### 1. Data Flow Diagram

The interaction sequence between the User, Frontend, and Backend is as follows:

1. **User Request:** The user submits a prompt via the Streamlit interface (`st.chat_input`). The Frontend dispatches a POST request containing the query payload to the Backend API.
2. **Backend Processing:** The Backend captures the request and initiates a multi-step processing pipeline (e.g., Intent Analysis -> SQL Generation -> Database Query -> Response Synthesis).
3. **Continuous Streaming:** Instead of waiting for the entire pipeline to resolve, the Backend continuously `yields` (pushes) small data chunks formatted as JSON strings back to the Frontend as each step concludes or as final answer tokens are generated.
4. **Frontend Parsing & Rendering:** Streamlit consumes the continuous stream, parses each JSON chunk, and evaluates the `type` property:
   * If `type == "status"`: Dynamically updates the execution progress inside the status container (`st.status`).
   * If `type == "token"`: Feeds individual text segments into `st.write_stream` to create a real-time typewriter effect.

### 2. JSON Data Structure Specification

The stream response delivered by the Backend consists of independent JSON lines. Each chunk must strictly adhere to the following schema:

#### Base Schema

```json
{
  "type": "string",
  "content": "string"
}