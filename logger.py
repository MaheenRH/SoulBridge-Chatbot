import logging
import os
from datetime import datetime

# =====================================
# 🧠 Logger Configuration
# =====================================

# Ensure logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# File name includes date
log_filename = os.path.join(LOG_DIR, f"chatbot_{datetime.now().strftime('%Y-%m-%d')}.log")

# Configure Python's logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()  # also print to console
    ]
)

logger = logging.getLogger("chatbot_logger")

# =====================================
# 🧩 Helper Functions
# =====================================

def log_interaction(session_id: str, user_message: str, bot_reply: str, emotion: str = None, is_crisis: bool = False):
    """Logs each interaction between the user and the chatbot."""
    if is_crisis:
        logger.warning(f"[CRISIS] Session: {session_id} | User: {user_message}")
    else:
        logger.info(f"Session: {session_id} | Emotion: {emotion} | User: {user_message} | Bot: {bot_reply}")

def log_error(session_id: str, error_msg: str):
    """Logs errors and exceptions."""
    logger.error(f"[ERROR] Session: {session_id} | {error_msg}")

def log_session_start(session_id: str):
    """Logs new session creation."""
    logger.info(f"🔹 New session started: {session_id}")

def log_session_end(session_id: str):
    """Logs when session ends or times out."""
    logger.info(f"🔸 Session ended: {session_id}")
