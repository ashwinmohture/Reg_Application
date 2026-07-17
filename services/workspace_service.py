from pathlib import Path
import json
import shutil
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent

WORKSPACE = BASE_DIR / "workspace"

WORKSPACE.mkdir(
    parents=True,
    exist_ok=True
)


# ----------------------------------------
# Create Project
# ----------------------------------------

def create_project(project_name):

    project_path = WORKSPACE / project_name

    project_path.mkdir(
        parents=True,
        exist_ok=True
    )

    folders = [
        "source",
        "chroma",
        "reports",
        "docs"
    ]

    for folder in folders:

        (project_path / folder).mkdir(
            exist_ok=True
        )

    metadata = {

        "project_name": project_name,
        "files": 0,
        "chunks": 0,
        "embedding": "",
        "llm": "",
        "security": "Not Scanned",
        "documentation": "Not Generated",
        "reports": 0,
        "last_indexed": datetime.now().strftime(
            "%d %b %Y %H:%M"
        )

    }

    with open(
        project_path / "metadata.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    return project_path


# ----------------------------------------
# Project Exists
# ----------------------------------------

def project_exists(project_name):

    return (
        WORKSPACE /
        project_name
    ).exists()


# ----------------------------------------
# List Projects
# ----------------------------------------

def list_projects():

    return sorted(

        item.name

        for item in WORKSPACE.iterdir()

        if item.is_dir()

    )


# ----------------------------------------
# Project Path
# ----------------------------------------

def get_project_path(project_name):

    return (
        WORKSPACE /
        project_name
    )


# ----------------------------------------
# Source Path
# ----------------------------------------

def get_source_path(project_name):

    return (
        WORKSPACE /
        project_name /
        "source"
    )


# ----------------------------------------
# Chroma Path
# ----------------------------------------
#
# On Windows, chromadb's HNSW index files (data_level0.bin, etc.) are
# memory-mapped by the OS. Deleting the persist directory in place
# fails with WinError 32 if any client (past or present, in this same
# process) still has it mapped, and retries don't reliably fix that.
#
# To avoid ever deleting a folder that might still be mapped, each
# index run gets its own versioned subfolder under "chroma/", and a
# small pointer file tracks which version is "current". Old versions
# are cleaned up on a best-effort basis only.

def get_chroma_root(project_name):

    return (
        WORKSPACE /
        project_name /
        "chroma"
    )


def _chroma_pointer_file(project_name):

    return get_chroma_root(project_name) / "current.txt"


def get_chroma_path(project_name):
    """
    Returns the active chroma DB folder for this project (the one
    pointed to by current.txt), or a default "v1" folder if none has
    been created yet.
    """

    root = get_chroma_root(project_name)
    pointer = _chroma_pointer_file(project_name)

    if pointer.exists():

        version = pointer.read_text(encoding="utf-8").strip()

        if version:

            return root / version

    return root / "v1"


def new_chroma_version_path(project_name):
    """
    Allocates a fresh, never-before-used chroma folder for a new index
    run. Does not touch or delete any existing version.
    """

    root = get_chroma_root(project_name)

    root.mkdir(
        parents=True,
        exist_ok=True
    )

    version = "v" + datetime.now().strftime("%Y%m%d%H%M%S%f")

    return root / version


def set_current_chroma_version(project_name, chroma_path):
    """
    Points current.txt at the given chroma folder, making it the one
    load_project_retriever() / get_chroma_path() will use from now on.
    """

    pointer = _chroma_pointer_file(project_name)

    pointer.write_text(
        chroma_path.name,
        encoding="utf-8"
    )


def cleanup_old_chroma_versions(project_name, keep_path):
    """
    Best-effort removal of stale chroma version folders other than
    keep_path. Any folder that's still locked (e.g. an open client
    from a previous session) is silently skipped and cleaned up on a
    later run instead of failing the current one.
    """

    root = get_chroma_root(project_name)

    if not root.exists():

        return

    for item in root.iterdir():

        if not item.is_dir():
            continue

        if item == keep_path:
            continue

        try:

            shutil.rmtree(item)

        except Exception:

            # Still locked - leave it for a future cleanup pass.
            pass


# ----------------------------------------
# Metadata
# ----------------------------------------

def get_metadata(project_name):

    metadata_file = (
        WORKSPACE /
        project_name /
        "metadata.json"
    )

    if not metadata_file.exists():

        return {}

    with open(
        metadata_file,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ----------------------------------------
# Update Metadata
# ----------------------------------------

def update_metadata(
    project_name,
    files,
    chunks,
    embedding,
    llm,
    security="Not Scanned",
    documentation="Not Generated",
    reports=0
):

    metadata = {

        "project_name": project_name,
        "files": files,
        "chunks": chunks,
        "embedding": embedding,
        "llm": llm,
        "security": security,
        "documentation": documentation,
        "reports": reports,
        "last_indexed": datetime.now().strftime(
            "%d %b %Y %H:%M"
        )

    }

    metadata_file = (
        WORKSPACE /
        project_name /
        "metadata.json"
    )

    with open(
        metadata_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )


# ----------------------------------------
# Clear Source
# ----------------------------------------

def clear_source(project_name):

    source = get_source_path(
        project_name
    )

    if source.exists():

        shutil.rmtree(source)

    source.mkdir(
        parents=True,
        exist_ok=True
    )


# ----------------------------------------
# Current Project
# ----------------------------------------

def set_current_project(project_name):

    return project_name


# ----------------------------------------
# Validate Project
# ----------------------------------------

def is_valid_project(project_name):

    return (
        WORKSPACE /
        project_name
    ).exists()