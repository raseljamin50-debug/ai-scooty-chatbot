"""
All settings in one place.  You can change them here, or set an environment variable
with the same name (for example in the start.bat file).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


# ---------------------------------------------------------------- brand
BRAND_NAME = os.getenv("BRAND_NAME", "AI Scooty")

# !!! CHANGE THIS to the real customer-support direct phone number !!!
SUPPORT_PHONE = os.getenv("SUPPORT_PHONE", "1315415455git --version")

# ---------------------------------------------------------------- server
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# ---------------------------------------------------------------- knowledge base (a file for now,
# the database comes in the next version)
KNOWLEDGE_FILE = Path(os.getenv("KNOWLEDGE_FILE", BASE_DIR / "data" / "knowledge.json"))

# ---------------------------------------------------------------- Ollama (internal AI)
# USE_LLM=false  -> the bot answers only with the exact written answers (no AI wording at all).
USE_LLM = _bool("USE_LLM", True)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "30"))   # seconds
LLM_KEEP_ALIVE = os.getenv("LLM_KEEP_ALIVE", "30m")

# ---------------------------------------------------------------- chat
MAX_MESSAGE_CHARS = 500
