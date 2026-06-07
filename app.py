import sys
sys.stdout.reconfigure(encoding='utf-8')

import logging
import os
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes.debug import router as debug_router
from routes.chatbot import router as chatbot_router

# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)

log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'buglens.log'),
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
logging.getLogger().addHandler(file_handler)


# ==========================================
# JSON LOGGER
# ==========================================

class JSONFormatter(logging.Formatter):
    def format(self, record):
        import json
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        try:
            return json.dumps(payload)
        except Exception:
            return str(payload)


json_handler = RotatingFileHandler(
    os.path.join(log_dir, 'buglens.json.log'),
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)
json_handler.setLevel(logging.INFO)
json_handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(json_handler)


# ==========================================
# FASTAPI APP
# ==========================================

base_dir = os.path.dirname(__file__)

app = FastAPI(
    title="BugLens AI Debugger",
    description="AI-powered Python code debugger using Groq LLM",
    version="2.0.0"
)

templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")

# Routers
app.include_router(debug_router, prefix="/debug", tags=["Debug"])
app.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])


# ==========================================
# PAGES
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    from chat_history import load_history
    history = load_history()
    return templates.TemplateResponse(request=request, name="chat.html", context={"history": history})


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    reload = os.environ.get("DEV", "false").strip().lower() in ("1", "true", "yes")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=reload, log_level="info")
