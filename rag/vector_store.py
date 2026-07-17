from pathlib import Path
import gc

import chromadb
from langchain_chroma import Chroma

from services.workspace_service import (
    new_chroma_version_path,
    set_current_chroma_version,
    cleanup_old_chroma_versions,
)


def _release_chroma_client():
    """
    Chromadb caches PersistentClient instances at the process level
    (SharedSystemClient). Clearing the cache lets any client from a
    previous session (e.g. one opened by the retriever) be garbage
    collected instead of continuing to hold the old chroma folder's
    files open/mapped.
    """
    try:
        chromadb.api.client.SharedSystemClient.clear_system_cache()
    except Exception:
        pass
    gc.collect()


def create_vector_store(
    chunks,
    embedding_model,
    project_name
):
    """
    Creates a Chroma database for a specific project.

    Each call writes to a brand new, uniquely-named folder rather than
    deleting and reusing the previous one. On Windows, chromadb's HNSW
    index files are memory-mapped, so deleting an in-use folder can
    fail with WinError 32 even after the client object is gone. Using
    a fresh folder every time sidesteps that entirely; the previous
    folder is only removed afterwards, best-effort, once it's no
    longer needed.
    """

    _release_chroma_client()

    chroma_path = new_chroma_version_path(
        project_name
    )

    chroma_path.mkdir(
        parents=True,
        exist_ok=True
    )
    safe_collection = (
        project_name
        .strip()
        .replace(" ", "_")
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=str(chroma_path),
        collection_name=safe_collection
    )

    # Only now that the new DB exists do we switch project pointer
    # over to it, then try to clean up old version(s) - if a stale
    # one is still locked, it's simply left for next time.
    set_current_chroma_version(project_name, chroma_path)
    _release_chroma_client()
    cleanup_old_chroma_versions(project_name, chroma_path)

    return vector_store