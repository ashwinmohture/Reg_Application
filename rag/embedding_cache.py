import hashlib
import json
import sqlite3
from pathlib import Path
from threading import Lock


BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_PATH = BASE_DIR / "database" / "embedding_cache.db"

CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

_lock = Lock()


def _connect():

    conn = sqlite3.connect(
        str(CACHE_PATH),
        check_same_thread=False
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS embedding_cache (
            cache_key TEXT PRIMARY KEY,
            vector TEXT NOT NULL
        )
        """
    )

    conn.commit()

    return conn


class EmbeddingCache:
    """
    Persists embedding vectors on disk, keyed by a hash of
    (model_name, text). Two things this exists for:

    1. Quota is precious on free tiers (e.g. Gemini's free tier caps
       out at 1000 embed_content calls/day). Without a cache, retrying
       a failed/partial indexing run re-embeds every chunk from
       scratch, including ones that already succeeded and consumed
       quota last time.
    2. Re-indexing an unchanged project (or a project that shares
       files with another) becomes instant for the unchanged portion.

    Cache entries are scoped by model name, so switching embedding
    providers/models naturally misses the cache instead of returning
    vectors from a different embedding space.
    """

    def __init__(self, model_name: str):

        self._model_name = model_name
        self._conn = _connect()

    def _key(self, text: str) -> str:

        raw = f"{self._model_name}::{text}".encode("utf-8")

        return hashlib.sha256(raw).hexdigest()

    def get(self, text: str):

        key = self._key(text)

        with _lock:

            row = self._conn.execute(
                "SELECT vector FROM embedding_cache WHERE cache_key = ?",
                (key,)
            ).fetchone()

        if row is None:
            return None

        return json.loads(row[0])

    def set(self, text: str, vector):

        key = self._key(text)
        payload = json.dumps(vector)

        with _lock:

            self._conn.execute(
                """
                INSERT INTO embedding_cache (cache_key, vector)
                VALUES (?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET vector = excluded.vector
                """,
                (key, payload)
            )

            self._conn.commit()