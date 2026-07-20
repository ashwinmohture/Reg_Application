import logging
import re
import time

from langchain_core.embeddings import Embeddings


logger = logging.getLogger(__name__)


def _safe_log(level, msg):
    try:
        logger.log(level, msg)
    except OSError:
        # See rag/embeddings.py::_safe_log - Windows console pipe can
        # go away mid-run; never let a log line crash the app.
        pass


_RETRY_DELAY_PATTERN = re.compile(r"retryDelay['\"]?\s*[:=]\s*['\"]?(\d+)")
_QUOTA_ERROR_MARKERS = ("RESOURCE_EXHAUSTED", "429", "rate limit", "Too Many Requests")

# Markers that indicate the quota is a DAILY (or otherwise long-window)
# cap rather than a per-minute one. Retrying a request against a
# daily cap is pointless - the API's reported "retryDelay" for these
# is often misleadingly short (e.g. 59s) even though the quota won't
# actually refill until the next day, so we must not treat it like a
# normal rate-limit retry.
_DAILY_QUOTA_MARKERS = ("PerDay", "per day", "daily")


class DailyQuotaExceededError(RuntimeError):
    """Raised when the provider's daily (not per-minute) quota is hit."""
    pass


class RateLimitedEmbeddings(Embeddings):
    """
    Wraps a LangChain Embeddings provider (Gemini, Mistral, ...) to:

    1. Throttle outgoing requests to stay under the provider's
       requests-per-minute quota (e.g. Gemini's free tier allows only
       100 embed_content calls/min - large codebases produce far more
       chunks than that, and the default LangChain wrapper fires them
       off with no pacing, causing 429 RESOURCE_EXHAUSTED).
    2. Automatically retry on per-minute quota/rate-limit errors with
       backoff, honoring the "retryDelay" the API reports when present.
    3. Fail fast (no retry) on a DAILY quota error, since no amount of
       throttling or retrying within the same run can get past it.

    This trades speed for reliability: a large project will simply
    take longer to index (spaced out under the quota) instead of
    failing outright partway through - up to the point of the
    provider's daily cap, at which point it stops cleanly instead of
    retrying forever.
    """

    def __init__(
        self,
        embedding: Embeddings,
        requests_per_minute: int = 90,
        max_retries: int = 6,
        progress_callback=None,
        cache=None,
        fallback=None,
    ):
        self._embedding = embedding
        self._min_interval = 60.0 / max(requests_per_minute, 1)
        self._max_retries = max_retries
        self._last_call = 0.0
        # Optional callable(done: int, total: int) for UI progress bars.
        self._progress_callback = progress_callback
        # Optional EmbeddingCache - see rag/embedding_cache.py. When
        # set, previously-embedded text is served from disk instead
        # of spending API quota on it again.
        self._cache = cache
        # Optional second RateLimitedEmbeddings to switch to, for the
        # rest of this run and all future calls, if the primary
        # provider hits its DAILY quota mid-job. A single up-front
        # "does this key work" test call isn't enough to guarantee a
        # provider survives a large bulk job (e.g. 5000+ chunks) - if
        # the daily cap is hit 900 chunks in, we don't want to abort
        # the whole indexing run when a working fallback is available.
        self._fallback = fallback

    def _switch_to_fallback(self, reason: str):

        if self._fallback is None:
            return False

        _safe_log(
            logging.WARNING,
            f"Primary embedding provider exhausted ({reason}). "
            f"Switching to fallback provider for the rest of this run."
        )

        # Swap this wrapper to behave exactly like the fallback from
        # here on (including its own throttling/cache/fallback-of-its-
        # own, if any), so every subsequent call - and any already-
        # in-flight loop in embed_documents - uses it transparently.
        self._embedding = self._fallback._embedding
        self._min_interval = self._fallback._min_interval
        self._cache = self._fallback._cache
        self._fallback = self._fallback._fallback

        return True

    def _throttle(self):

        elapsed = time.monotonic() - self._last_call
        wait = self._min_interval - elapsed

        if wait > 0:
            time.sleep(wait)

        self._last_call = time.monotonic()

    def _parse_retry_delay(self, message: str):

        match = _RETRY_DELAY_PATTERN.search(message)

        if match:
            return int(match.group(1)) + 1  # small safety margin

        return None

    def _is_quota_error(self, message: str) -> bool:

        return any(marker in message for marker in _QUOTA_ERROR_MARKERS)

    def _is_daily_quota_error(self, message: str) -> bool:

        return any(marker in message for marker in _DAILY_QUOTA_MARKERS)

    def _embed_one(self, text: str):

        if self._cache is not None:

            cached = self._cache.get(text)

            if cached is not None:
                return cached

        attempt = 0

        while True:

            self._throttle()

            try:

                vector = self._embedding.embed_query(text)

                if self._cache is not None:
                    self._cache.set(text, vector)

                return vector

            except Exception as e:

                message = str(e)

                if not self._is_quota_error(message):
                    raise

                if self._is_daily_quota_error(message):

                    if self._switch_to_fallback(message[:120]):
                        # Retry this same text immediately against
                        # whatever we just switched to.
                        continue

                    raise DailyQuotaExceededError(
                        "Daily embedding quota exceeded for this "
                        "provider's free tier, and no fallback "
                        "provider is configured/available. Retrying "
                        "won't help - this resets once per day, not "
                        "per minute. Options: (1) wait for the daily "
                        "quota to reset, (2) switch embedding "
                        "provider in Settings (e.g. to Mistral), or "
                        "(3) enable billing on your Google AI Studio "
                        f"project to raise the limit. Original error: {message}"
                    ) from e

                attempt += 1

                if attempt > self._max_retries:
                    raise RuntimeError(
                        f"Embedding provider rate limit exceeded after "
                        f"{self._max_retries} retries. Try again later, "
                        f"lower the requests-per-minute in Settings, or "
                        f"switch embedding provider. Original error: {message}"
                    ) from e

                delay = self._parse_retry_delay(message) or min(
                    60, 2 ** attempt
                )

                _safe_log(
                    logging.WARNING,
                    f"Embedding rate-limited (attempt {attempt}/"
                    f"{self._max_retries}), retrying in {delay}s..."
                )

                time.sleep(delay)

    def embed_documents(self, texts):

        results = []
        total = len(texts)

        for i, text in enumerate(texts):

            results.append(self._embed_one(text))

            if self._progress_callback:
                self._progress_callback(i + 1, total)

        return results

    def embed_query(self, text):

        return self._embed_one(text)