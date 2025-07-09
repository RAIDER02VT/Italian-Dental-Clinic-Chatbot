from fastapi import APIRouter,HTTPException
from app.schemas.chat import ChatRequest
from app.services.ask_gpt import ask_gpt
import logging

router = APIRouter()

@router.post("/chat")
async def chat_route(request: ChatRequest):
    try:
        print("📥 Messaggio ricevuto:", request.message)  # LOG
        if not request.message.strip():
            raise HTTPException(400, "Il messaggio non può essere vuoto")
        reply = ask_gpt(request.message)
        return {"risposta": reply}
    
    except HTTPException as httpe:
       raise httpe
    except Exception as e:
       logging.exception("Errore durante la generazione della risposta GPT")
       raise HTTPException(500, "Si è verificato un errore interno. Riprova più tardi.")