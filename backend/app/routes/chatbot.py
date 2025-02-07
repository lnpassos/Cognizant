from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.bot.chatbot import Chatbot

router = APIRouter()
# Set as an environment variable / (My personal Key with $10)
API_KEY = "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"

# Initialize the Chatbot
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
            response = chatbot.help_mode()  # Retorna ao menu se não houver mensagem
    elif request.chatMode == "free":
        response = chatbot.free_chat_mode(request.message)
    else:
        raise HTTPException(status_code=400, detail="Modo de chat inválido.")

    return {"reply": response}
