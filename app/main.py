"""AI Scooty chatbot - web server (FastAPI)."""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import config
from . import llm
from .matcher import KnowledgeBase
from .text_utils import has_bengali, tokens

kb = KnowledgeBase(config.KNOWLEDGE_FILE)

STARTER_QUESTIONS = [
    "What is AI Scooty?",
    "Who is the founder of AI Scooty?",
    "How much does AI Scooty cost?",
    "Can it run in the rain?",
    "How can I buy AI Scooty?",
]

OUT_OF_SCOPE = (
    "Sorry, I can only answer questions about AI Scooty, and I don't have an answer for that. "
    "For anything else, please call our customer support directly: {phone}"
)
NO_INFO_ABOUT_SCOOTY = (
    "Sorry, I don't have that information about AI Scooty yet. "
    "Please call our customer support directly and they will help you: {phone}"
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if config.USE_LLM:
        asyncio.create_task(llm.warm_up())      # load the model in the background
    yield


app = FastAPI(title="AI Scooty Assistant", lifespan=lifespan)


class Turn(BaseModel):
    role: str
    content: str = Field(max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=config.MAX_MESSAGE_CHARS)
    history: list[Turn] = Field(default_factory=list, max_length=40)


def _fill(text: str) -> str:
    return text.replace("{support_phone}", config.SUPPORT_PHONE)


def _reply(answer: str, kind: str, intent: str | None = None, score: float = 0.0,
           source: str = "written", suggestions: list[str] | None = None) -> dict:
    return {"answer": answer, "kind": kind, "intent": intent, "score": round(score, 3),
            "source": source, "suggestions": suggestions or []}


async def _answer_for(intent_id: str, score: float) -> dict:
    intent = kb.by_id[intent_id]
    written = _fill(intent["answer"])
    kind = "smalltalk" if intent_id in ("greeting", "thanks", "goodbye") else "answer"
    if intent.get("use_llm", True) and config.USE_LLM:
        nice = await llm.rephrase(intent["question"], written, intent.get("must_include", []))
        if nice:
            return _reply(nice, kind, intent_id, score, source="ollama")
    return _reply(written, kind, intent_id, score)


@app.post("/api/chat")
async def chat(req: ChatRequest):
    text = req.message.strip()

    # 1) Bangla typed -> tell them English only (for now)
    if has_bengali(text):
        return _reply(_fill(kb.by_id["language"]["answer"]), "answer", "language", 1.0)

    result = kb.match(text)

    # 2) Short follow-up ("and the license?") -> try together with the previous question
    if result.status != "confident" and len(tokens(text)) <= 3:
        previous = [t.content for t in req.history if t.role == "user"]
        if previous:
            combined = kb.match(previous[-1] + " " + text)
            if combined.status == "confident":
                result = combined

    # 3) Sure -> answer
    if result.status == "confident":
        return await _answer_for(result.intent_id, result.score)

    # 4) Not sure -> ask "did you mean ...?"  (never guess)
    if result.status == "suggest":
        ids = [i for i, _ in result.candidates if i not in ("greeting", "thanks", "goodbye")][:3]
        if ids:
            return _reply("I'm not completely sure what you mean. Did you mean one of these?",
                          "suggest", None, result.score,
                          suggestions=[kb.by_id[i]["question"] for i in ids])

    # 5) Nothing fits -> out of scope, give support phone
    mentions_product = any(t in ("scooty", "ai") for t in tokens(text))
    template = NO_INFO_ABOUT_SCOOTY if mentions_product else OUT_OF_SCOPE
    return _reply(template.format(phone=config.SUPPORT_PHONE), "fallback", None, result.score)


@app.get("/api/config")
async def get_config():
    return {"brand": config.BRAND_NAME, "support_phone": config.SUPPORT_PHONE,
            "starters": STARTER_QUESTIONS}


@app.get("/api/health")
async def health():
    return {"status": "ok", "questions_in_knowledge_base": len(kb.intents),
            "ollama": await llm.status()}


@app.get("/")
async def home():
    return FileResponse(config.BASE_DIR / "static" / "index.html")


app.mount("/static", StaticFiles(directory=config.BASE_DIR / "static"), name="static")
