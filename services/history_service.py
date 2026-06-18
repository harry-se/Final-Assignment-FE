import os
import requests
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")

def get_conversation():
    """
    Fetch list of all active conversations from backend
    
    Returns:
        list: List of conversation IDs
    """
    try:
        response = requests.get(
            f"{BACKEND_URL}/conversations",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data.get("conversations", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching conversations: {e}")
        return []


def get_conversation_by_id(conversation_id):
    """
    Fetch message history for a specific conversation from backend
    
    Args:
        conversation_id: The ID of the conversation
        
    Returns:
        dict: Conversation data with messages, or None if not found
    """
    try:
        response = requests.get(
            f"{BACKEND_URL}/conversations/{conversation_id}/messages",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching conversation {conversation_id}: {e}")
        return None


def delete_conversation(conversation_id):
    """
    Delete a conversation from backend
    
    Args:
        conversation_id: The ID of the conversation to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        response = requests.delete(
            f"{BACKEND_URL}/conversations/{conversation_id}",
            timeout=10
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting conversation {conversation_id}: {e}")
        return False


