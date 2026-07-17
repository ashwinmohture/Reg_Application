from pathlib import Path
import os

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

from services.settings_service import get_setting

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def get_llm():

    return ChatMistralAI(
        model="mistral-large-latest",
        api_key=os.getenv("MISTRALAI_API_KEY"),
        temperature=get_setting("llm_temperature"),
    )