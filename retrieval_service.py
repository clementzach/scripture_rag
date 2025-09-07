from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import chromadb
import logging

# Local imports
from config import (
    DATA_PATH,
    CHROMA_PATH,
    OPENAI_API_KEY,
)

# Optional config values (fallbacks if missing)
try:
    from config import (
        CHROMA_USE_HTTP,  # type: ignore
        CHROMA_SERVER_HOST,  # type: ignore
        CHROMA_SERVER_HTTP_PORT,  # type: ignore
    )
except Exception:
    CHROMA_USE_HTTP = False  # type: ignore
    CHROMA_SERVER_HOST = "localhost"  # type: ignore
    CHROMA_SERVER_HTTP_PORT = 8000  # type: ignore

try:
    from config import HYP_QUEST_COLLECTION_NAME  # type: ignore
except Exception:
    # Fallback to a generic collection name if hypothetical-questions collection is undefined
    from config import COLLECTION_NAME as HYP_QUEST_COLLECTION_NAME  # type: ignore

from llm_retrieval import get_all_scriptures, get_scriptures_string


class RetrieveRequest(BaseModel):
    question: str
    generative_model: Optional[str] = "gpt-4o-mini"


class RetrieveResponse(BaseModel):
    scriptures_string: str


app = FastAPI(title="Scripture Retrieval Service", version="1.0.0")


# Globals initialized at startup
SCRIPTURE_DICT = None
CHROMA_COLLECTION = None

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))


def init_chroma_collection():
    """Initialize and return a Chroma collection for hypothetical questions (if configured)."""
    if CHROMA_USE_HTTP:
        client = chromadb.HttpClient(host=CHROMA_SERVER_HOST, port=CHROMA_SERVER_HTTP_PORT)
    else:
        # Local persistent client
        os.makedirs(CHROMA_PATH, exist_ok=True)
        client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Ensure the target collection exists
    return client.get_or_create_collection(name=HYP_QUEST_COLLECTION_NAME)


@app.on_event("startup")
def on_startup():
    global SCRIPTURE_DICT, CHROMA_COLLECTION

    # Make sure OpenAI key is present in env for downstream calls
    if OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    # Load scriptures index
    SCRIPTURE_DICT = get_all_scriptures(DATA_PATH)

    # Initialize Chroma collection (either HTTP server or local persistence)
    CHROMA_COLLECTION = init_chroma_collection()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/retrieve", response_model=RetrieveResponse)
def retrieve(req: RetrieveRequest):
    if SCRIPTURE_DICT is None or CHROMA_COLLECTION is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        scriptures_string = get_scriptures_string(
            scripture_dict=SCRIPTURE_DICT,
            question=req.question,
            generative_model=req.generative_model or "gpt-4o-mini",
            collection=CHROMA_COLLECTION,
        )
        return RetrieveResponse(scriptures_string=scriptures_string)
    except Exception as e:
        logger.exception("Error during retrieval for question: %s", req.question)
        raise HTTPException(status_code=502, detail=f"Retrieval failed: {e}")


# For local debugging: `uvicorn retrieval_service:app --reload --port 8001`
