# app.py
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
backend_url = os.getenv("BACKEND_URL","")

st.markdown("""
# 🤖 AI Agent for Customer Service Analytics

This project is an AI-powered customer service analytics assistant that helps users query, analyze, and visualize customer service data through natural language conversations.

### ✨ Key Features
- Natural language chat interface
- Intelligent data retrieval and analysis
- AI Agent workflow
- Conversation history management


### 📂 Source Code
https://github.com/harry-se/Final-Assignment-FE
""")