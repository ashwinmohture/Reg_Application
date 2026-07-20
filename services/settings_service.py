# Application settings: RAG parameters + API key management
import re
import time
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

    # Embedding request throttling - prevents 429 RESOURCE_EXHAUSTED
    # errors on large projects. Gemini's free tier allows 100
    # embed_content requests/minute; default is set a bit under that
    # as a safety margin. Raise this if you're on a paid tier.
    "embedding_requests_per_minute": 90,

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


def _set_key_manual(env_var: str, value: str):
    """
    Fallback writer that avoids dotenv's set_key() entirely.

    set_key() writes a temp file then calls os.replace() to swap it
    in atomically - which is the safer approach in general, but on
    Windows os.replace() raises PermissionError/WinError 5 if
    anything else (an editor, OneDrive, antivirus, a stray leftover
    process) briefly has the destination file locked. Rather than
    fail the whole save when that happens, fall back to a plain
    read-modify-write of the file in place.
    """

    lines = []

    if ENV_PATH.exists():

        with open(ENV_PATH, "r", encoding="utf-8") as file:
            lines = file.readlines()

    pattern = re.compile(rf"^\s*{re.escape(env_var)}\s*=")
    found = False

    for i, line in enumerate(lines):

        if pattern.match(line):
            lines[i] = f"{env_var}={value}\n"
            found = True
            break

    if not found:
        lines.append(f"{env_var}={value}\n")

    with open(ENV_PATH, "w", encoding="utf-8") as file:
        file.writelines(lines)


def _write_env_key(env_var: str, value: str, max_retries: int = 3):

    last_error = None

    for attempt in range(max_retries):

        try:

            set_key(
                str(ENV_PATH),
                env_var,
                value
            )

            return

        except (PermissionError, OSError) as e:

            last_error = e
            # Brief pause - most Windows file locks (editor autosave,
            # antivirus scan, OneDrive sync) release within a second.
            time.sleep(0.4 * (attempt + 1))

    # dotenv's atomic write kept failing - fall back to a direct
    # in-place write, which doesn't need the os.replace() step that
    # was getting blocked.
    try:

        _set_key_manual(env_var, value)

    except OSError as e:

        raise PermissionError(
            f"Could not write {env_var} to {ENV_PATH}. The file may "
            f"be open in another program, marked read-only, or "
            f"locked by antivirus/OneDrive sync. Close any programs "
            f"that have .env open, make sure it isn't read-only, and "
            f"try again. Original error: {last_error or e}"
        ) from e


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

        _write_env_key(env_var, value)

        os.environ[env_var] = value

        updated.append(env_var)

    return updated