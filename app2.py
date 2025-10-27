# app.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from chatbot_chain2 import MentalHealthChatbot

# =====================================================
# 🚀 FastAPI Initialization
# =====================================================
app = FastAPI(
    title="Mental Health Chatbot API",
    description="Empathetic, retrieval-augmented chatbot powered by LangChain + OpenAI",
    version="1.2.0",
)

# Enable CORS (frontend JS communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# 🤖 Initialize Chatbot (with RAG + Emotion detection)
# =====================================================
chatbot = MentalHealthChatbot()


# =====================================================
# 📦 Request Schema
# =====================================================
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


# =====================================================
# 💬 Chat Endpoint
# =====================================================
@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    """
    Handles chat messages from the frontend.
    Accepts user message + optional session_id.
    Returns chatbot response + active session_id.
    """
    return chatbot.chat(message=request.message, session_id=request.session_id)


# =====================================================
# 🧹 End Session Endpoint
# =====================================================
@app.post("/end-session")
def end_session(request: ChatRequest):
    """
    Ends the chat session and clears stored memory.
    """
    return chatbot.end_session(request.session_id)


# =====================================================
# 🏠 Root Endpoint
# =====================================================
@app.get("/")
def root():
    return {
        "message": "Welcome to the Mental Health Chatbot API 🧠💬",
        "docs": "Visit /docs for API interface",
    }
