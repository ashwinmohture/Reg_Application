# Application settings: RAG parameters + API key management
from pathlib import Path
import json
import os

from dotenv import load_dotenv, set_key


BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = BASE_DIR / "config"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
ENV_PATH = BASE_DIR / ".env"

CONFIG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# Make sure keys already in .env are loaded into the process before
# anything reads os.getenv(...).
load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)


DEFAULT_SETTINGS = {

    # "auto" tries Gemini first and falls back to Mistral (existing
    # behaviour). "gemini" / "mistral" force a single provider.
    "embedding_provider": "auto",

    "llm_temperature": 0.2,

    # Code splitting
    "chunk_size": 500,
    "chunk_overlap": 100,

    # Retrieval
    "top_k": 5,

}

# Keys the UI is allowed to manage. Values are (env_var_name, label).
MANAGED_KEYS = {
    "google_api_key": ("GOOGLE_API_KEY", "Google Gemini API Key"),
    "mistral_api_key": ("MISTRALAI_API_KEY", "Mistral API Key"),
    "github_token": ("GITHUB_TOKEN", "GitHub Access Token"),
}


# ----------------------------------------
# RAG / model settings
# ----------------------------------------

def load_settings():
    """
    Returns the current settings, merged over the defaults so a
    partially written / older settings.json never breaks the app.
    """

    settings = dict(DEFAULT_SETTINGS)

    if SETTINGS_FILE.exists():

        try:

            with open(
                SETTINGS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                saved = json.load(file)

            settings.update(saved)

        except (json.JSONDecodeError, OSError):

            # Corrupt or unreadable file - fall back to defaults
            # rather than crashing the app.
            pass

    return settings


def save_settings(new_settings):

    settings = load_settings()
    settings.update(new_settings)

    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            settings,
            file,
            indent=4
        )

    return settings


def get_setting(key, default=None):

    return load_settings().get(
        key,
        DEFAULT_SETTINGS.get(key, default)
    )


def reset_settings():

    if SETTINGS_FILE.exists():

        SETTINGS_FILE.unlink()

    return dict(DEFAULT_SETTINGS)


# ----------------------------------------
# API keys (.env)
# ----------------------------------------

def get_api_keys():
    """
    Returns current values for all managed keys, read fresh from the
    environment (not just what was last saved this session).
    """

    return {
        field: os.getenv(env_var, "")
        for field, (env_var, _label) in MANAGED_KEYS.items()
    }


def mask_key(value):
    """
    Shows just enough of a secret to recognise it without exposing it,
    e.g. "AIzaSyD1234567890" -> "AIza••••••••7890".
    """

    if not value:
        return ""

    if len(value) <= 8:
        return "•" * len(value)

    return f"{value[:4]}{'•' * 8}{value[-4:]}"


def save_api_keys(**keys):
    """
    Writes provided keys to .env and refreshes os.environ immediately,
    so callers elsewhere in the running app (get_llm(), etc.) see the
    new values without a restart. Pass field=None or field="" to leave
    an existing key untouched (avoids clobbering a saved key with a
    blank UI field).
    """

    if not ENV_PATH.exists():
        ENV_PATH.touch()

    updated = []

    for field, value in keys.items():

        if not value:
            continue

        env_var, _label = MANAGED_KEYS[field]

        set_key(
            str(ENV_PATH),
            env_var,
            value
        )

        os.environ[env_var] = value

        updated.append(env_var)

    return updated