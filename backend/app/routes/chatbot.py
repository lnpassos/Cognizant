# app/endpoints/chatbot.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.bot.chatbot import Chatbot

router = APIRouter()
API_KEY = "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"

# Instanciar o chatbot
chatbot = Chatbot(api_key=API_KEY)

class ChatRequest(BaseModel):
    message: str
    chatMode: str


@router.post("/chatbot")
async def chat(request: ChatRequest):
    if request.chatMode == "help":
        if request.message.strip() in ["1", "2"]:
            response = chatbot.help_mode(request.message.strip())
        else:
            response = chatbot.help_mode()
    elif request.chatMode == "free":
        response = chatbot.free_chat_mode(request.message)
    else:
        raise HTTPException(status_code=400, detail="Modo de chat inválido.")

    return {"reply": response}
