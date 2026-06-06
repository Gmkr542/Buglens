from fastapi import APIRouter
from pydantic import BaseModel
from chat_history import append_message, load_history, clear_history

router = APIRouter()


# ==========================================
# MODELS
# ==========================================

class ChatRequest(BaseModel):
    message: str


# ==========================================
# BOT LOGIC
# ==========================================

def generate_bot_reply(user_message: str) -> str:
    normalized = user_message.strip().lower()
    if not normalized:
        return "Please type something so I can respond."
    if "hello" in normalized or "hi" in normalized:
        return "Hello! I am your chatbot. How can I help you today?"
    if "help" in normalized:
        return "I can keep track of our conversation and respond to simple questions."
    if "name" in normalized:
        return "I am a simple chatbot built with FastAPI."
    if "time" in normalized:
        return "I don't have a real clock, but I can keep our chat history for you."
    return "That sounds interesting. Tell me more so I can help."


# ==========================================
# ROUTES
# ==========================================

@router.post("/")
async def chat(payload: ChatRequest):
    """Send a message and get a bot reply."""
    append_message("user", payload.message)
    reply = generate_bot_reply(payload.message)
    append_message("bot", reply)
    return {"reply": reply, "history": load_history()}


@router.post("/clear")
async def clear():
    """Clear the full chat history."""
    return {"history": clear_history()}


@router.get("/history")
async def history():
    """Return the current chat history."""
    return {"history": load_history()}
