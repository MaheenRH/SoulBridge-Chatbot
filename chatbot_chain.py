import os
import uuid
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from transformers import pipeline
from logger import log_interaction, log_error, log_session_start, log_session_end
from typing import Optional

# ✅ Load environment variables
load_dotenv()


class MentalHealthChatbot:
    def __init__(self):
        """Initialize models, prompt templates, and persistent session store."""
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)

        self.emotion_classifier = pipeline(
            "sentiment-analysis",
            model="j-hartmann/emotion-english-distilroberta-base"
        )

        # 💾 Persistent memory file
        self.memory_file = Path("data/memory_store.json")
        self.memory_file.parent.mkdir(exist_ok=True)

        # 💾 In-memory session store
        self.sessions = {}

        # Load memory from disk if available
        self.load_memory()

        self.template = """
        You are a compassionate mental health support assistant.
        The user currently feels {emotion}.
        Your task:
        1. Respond with empathy, warmth, and encouragement.
        2. Provide gentle advice using evidence-based self-care techniques.
        3. Avoid diagnostic or medical claims.

        Chat history:
        {history}

        User: {user_message}
        Assistant:
        """

        self.prompt = PromptTemplate(
            input_variables=["emotion", "history", "user_message"],
            template=self.template
        )

  
    def chat(self, message: str, session_id: Optional[str] = None):
        """Main chat handler. Manages sessions, detects emotion, and generates response."""
        try:
            # 1️⃣ Create or retrieve session
            if not session_id:
                session_id = str(uuid.uuid4())
                self.sessions[session_id] = ConversationBufferMemory(return_messages=True)
                log_session_start(session_id)
            elif session_id not in self.sessions:
                self.sessions[session_id] = ConversationBufferMemory(return_messages=True)
                log_session_start(session_id)

            memory = self.sessions[session_id]
            lower_msg = message.lower()

            # 2️⃣ Crisis detection
            crisis_keywords = [
                "suicide", "kill myself", "end my life",
                "hurt myself", "no reason to live"
            ]
            if any(word in lower_msg for word in crisis_keywords):
                crisis_response = (
                    "🚨 It sounds like you might be in crisis. You are *not alone*.\n"
                    "Please reach out for immediate help:\n"
                    "- 📞 988 Suicide & Crisis Lifeline (U.S.)\n"
                    "- 🌍 https://findahelpline.com\n"
                    "You deserve care and safety ❤️"
                )
                log_interaction(session_id, message, crisis_response, is_crisis=True)
                self.save_memory()
                return {"session_id": session_id, "response": crisis_response}

            # 3️⃣ Greeting detection
            greetings = ["hello", "hi", "hey", "how are you", "good morning", "good evening"]
            if any(word in lower_msg for word in greetings):
                short_reply = "Hi there! 😊 I'm doing well and happy to chat. How are you feeling today?"
                log_interaction(session_id, message, short_reply)
                self.save_memory()
                return {"session_id": session_id, "response": short_reply}

          
            emotion = self.emotion_classifier(message)[0]["label"]

         
            chain = RunnableSequence(self.prompt | self.llm)

            inputs = {
                "emotion": emotion,
                "history": memory.buffer_as_str if hasattr(memory, "buffer_as_str") else "",
                "user_message": message,
            }

            result = chain.invoke(inputs)

       
            log_interaction(session_id, message, result.content, emotion)
            self.save_memory()

            return {
                "session_id": session_id,
                "response": f"({emotion.capitalize()}) {result.content}",
            }

        except Exception as e:
            print(f"[Chat Error] {e}")  # 👈 Print real issue for debugging
            log_error(session_id or "N/A", str(e))
            return {
                "session_id": session_id,
                "response": "⚠️ Sorry, something went wrong. Please try again later.",
            }

    def save_memory(self):
        """Save all session memory to disk."""
        try:
            data = {
                sid: mem.buffer_as_str if hasattr(mem, "buffer_as_str") else ""
                for sid, mem in self.sessions.items()
            }
            with open(self.memory_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Save Memory Error] {e}")

    def load_memory(self):
        """Load session memory from disk."""
        if not self.memory_file.exists():
            return
        try:
            with open(self.memory_file, "r") as f:
                data = json.load(f)
            for sid, history in data.items():
                mem = ConversationBufferMemory(return_messages=True)
                if history:
                    mem.chat_memory.add_user_message(history)
                self.sessions[sid] = mem
        except Exception as e:
            print(f"[Load Memory Error] {e}")

   
    def end_session(self, session_id: str):
        """Ends a chat session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            log_session_end(session_id)
            self.save_memory()  # 💾 Persist changes
            return {"message": f"Session {session_id} ended and cleared."}
        return {"message": "No active session found."}
