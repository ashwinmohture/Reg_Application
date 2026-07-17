# GitHub repository service
# GitHub repository service
from pathlib import Path
import os
import shutil

from git import Repo


def clone_repository(repo_url: str, workspace: Path):

    repo_name = repo_url.rstrip("/").split("/")[-1]

    destination = workspace / repo_name

    if destination.exists():
        shutil.rmtree(destination)

    token = os.getenv("GITHUB_TOKEN")

    clone_url = repo_url

    if token and repo_url.startswith("https://github.com/"):

        # Inject the token for private-repo access. Kept out of any
        # exception message / log line so it never leaks to the UI.
        clone_url = repo_url.replace(
            "https://github.com/",
            f"https://{token}@github.com/"
        )

    try:

        Repo.clone_from(
            clone_url,
            destination
        )

    except Exception as e:

        # Strip the token out of the error message before it can
        # surface anywhere (Streamlit UI, logs, reports).
        safe_message = str(e).replace(token, "***") if token else str(e)

        raise RuntimeError(
            f"Failed to clone repository: {safe_message}"
        ) from e

    return destination