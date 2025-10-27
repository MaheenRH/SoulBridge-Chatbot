# app.py
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from chatbot_chain import MentalHealthChatbot
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# ✅ This must exist and be named exactly `app`
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot = MentalHealthChatbot()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
def read_root():
    return FileResponse(os.path.join("frontend", "index.html"))

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    return chatbot.chat(message=request.message, session_id=request.session_id)

@app.post("/end-session")
def end_session(request: ChatRequest):
    return chatbot.end_session(request.session_id)
