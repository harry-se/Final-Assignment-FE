# Call Center Analytics Agent — Frontend

Streamlit UI for the Call Center Analytics Agent.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Backend service running (see `Final-Assignment`)

## Setup

```bash
# 1. Install dependencies
uv sync

# 2. Copy env file
cp .env.example .env
```

Edit `.env`:

| Variable | Description |
|----------|-------------|
| `BACKEND_URL` | Backend API URL, e.g. `http://localhost:8000/api` |

## Run

```bash
uv run streamlit run main.py
```

App available at: `http://localhost:8501`

## Stop

`Ctrl+C` in terminal.
