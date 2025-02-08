from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.bot.chatbot import Chatbot
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

router = APIRouter()

""" 
    Here is the API key for testing purposes in this project. However, this is only for evaluation. 
    For better security, in a real production system, we can configure the API key using Docker, 
    Kubernetes Secrets, or directly as an environment variable on the server. 
"""

# Fetch the API key from the environment variable
API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the Chatbot with the API key
chatbot = Chatbot(api_key=API_KEY)


class ChatRequest(BaseModel):
    message: str
    chatMode: str


# Chatbot endpoint
@router.post("/chatbot")
async def chat(request: ChatRequest):
    if request.chatMode == "help":
        if request.message.strip() in ["1", "2"]:
            response = chatbot.help_mode(request.message.strip())
        else:
            response = chatbot.help_mode()  # Return to the menu if no message
    elif request.chatMode == "free":
        response = chatbot.free_chat_mode(request.message)
    else:
        raise HTTPException(status_code=400, detail="Invalid chat mode.")

    return {"reply": response}
