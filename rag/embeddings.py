import os
import logging
from pathlib import Path

from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_mistralai import MistralAIEmbeddings

from services.settings_service import get_setting


logger = logging.getLogger(__name__)


def _safe_log(level, msg):
    """
    Wrapper around logging calls.

    Root cause of the WinError 233 crash: on Windows, Streamlit's file
    watcher can tear down / detach the running script's stdout pipe while
    a long blocking call (like an embedding API request) is still in
    flight. If that happens, a later print()/log write raises
    OSError: [WinError 233] and crashes the whole request even though the
    "real" error (e.g. an API failure) is unrelated and already handled.

    We never want a *logging* statement to be the thing that crashes the
    app, so failures here are swallowed.
    """
    try:
        logger.log(level, msg)
    except OSError:
        # stdout/stderr pipe is gone (Streamlit rerun/watcher race on
        # Windows) - nothing useful we can do, just don't crash on it.
        pass


CURRENT_FILE = Path(__file__).resolve()
# rag/embeddings.py -> rag/ -> RepoMind-AI/   (project root)
# NOTE: previously this was CURRENT_FILE.parent.parent.parent, which points
# one directory too high (e.g. D:\xampp\htdocs\RAG instead of
# D:\xampp\htdocs\RAG\RepoMind-AI) and silently failed to load the .env
# file placed at the project root, leaving GOOGLE_API_KEY / MISTRALAI_API_KEY
# unset.
BASE_DIR = CURRENT_FILE.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)

if not ENV_PATH.exists():
    _safe_log(
        logging.WARNING,
        f".env not found at {ENV_PATH} - API keys must be set some other way."
    )


def get_embedding_model():

    google_key = os.getenv("GOOGLE_API_KEY")
    mistral_key = os.getenv("MISTRALAI_API_KEY")

    provider = get_setting("embedding_provider")  # "auto" | "gemini" | "mistral"

    # -----------------------------
    # Try Gemini First
    # -----------------------------
    if google_key and provider in ("auto", "gemini"):

        try:

            _safe_log(logging.INFO, "Using Google Gemini Embeddings...")

            embedding = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=google_key
            )

            # Test request
            embedding.embed_query("hello")

            _safe_log(logging.INFO, "Gemini Embeddings Ready")

            return embedding

        except Exception as e:

            _safe_log(logging.WARNING, f"Gemini failed: {e}")

            if provider == "gemini":
                raise RuntimeError(
                    f"Gemini embedding failed and provider is locked "
                    f"to 'gemini' in Settings: {e}"
                ) from e

            _safe_log(logging.INFO, "Switching to Mistral...")

    # -----------------------------
    # Fallback to Mistral
    # -----------------------------
    if mistral_key and provider in ("auto", "mistral"):

        try:

            embedding = MistralAIEmbeddings(
                model="mistral-embed",
                api_key=mistral_key
            )

            embedding.embed_query("hello")

            _safe_log(logging.INFO, "Mistral Embeddings Ready")

            return embedding

        except Exception as e:

            raise RuntimeError(
                f"Mistral embedding failed: {e}"
            ) from e

    raise RuntimeError(
        "No embedding provider available. "
        "Check GOOGLE_API_KEY / MISTRALAI_API_KEY and the provider "
        "selected in Settings."
    )