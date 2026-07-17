import os
import traceback
from pathlib import Path

from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_mistralai import MistralAIEmbeddings


# ---------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------

CURRENT_FILE = Path(__file__).resolve()

# RepoMind-AI/
BASE_DIR = CURRENT_FILE.parent.parent

ENV_PATH = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)


# ---------------------------------------------------
# Embedding Loader
# ---------------------------------------------------

def get_embedding_model():
    """
    Returns the best available embedding model.

    Priority:
        1. Google Gemini
        2. Mistral

    Returns:
        Embedding Model
    """

    google_key = os.getenv("GOOGLE_API_KEY")
    mistral_key = os.getenv("MISTRALAI_API_KEY")

    # ---------------------------------------------------
    # Try Google Gemini
    # ---------------------------------------------------

    if google_key:

        try:

            print("=" * 60)
            print("Loading Google Gemini Embeddings...")
            print("=" * 60)

            embedding = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=google_key
            )

            # Test the API immediately
            embedding.embed_query("Hello")

            print("✅ Google Gemini Embeddings Loaded")

            return embedding

        except Exception:

            print("=" * 60)
            print("❌ Failed to load Google Gemini")
            traceback.print_exc()
            print("=" * 60)

    # ---------------------------------------------------
    # Try Mistral
    # ---------------------------------------------------

    if mistral_key:

        try:

            print("=" * 60)
            print("Loading Mistral Embeddings...")
            print("=" * 60)

            embedding = MistralAIEmbeddings(
                model="mistral-embed",
                api_key=mistral_key
            )

            print("✅ Mistral Embeddings Loaded")

            return embedding

        except Exception:

            print("=" * 60)
            print("❌ Failed to load Mistral")
            traceback.print_exc()
            print("=" * 60)

    # ---------------------------------------------------
    # No Provider Available
    # ---------------------------------------------------

    raise RuntimeError(
        "\nNo embedding provider available.\n\n"
        "Please check:\n"
        "1. GOOGLE_API_KEY\n"
        "2. MISTRALAI_API_KEY\n"
        "3. .env file location\n"
    )


# ---------------------------------------------------
# Test
# ---------------------------------------------------

if __name__ == "__main__":

    model = get_embedding_model()

    print(model)