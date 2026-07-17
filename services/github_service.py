# GitHub repository service
from pathlib import Path
import shutil
from git import Repo


def clone_repository(repo_url: str, workspace: Path):

    repo_name = repo_url.rstrip("/").split("/")[-1]

    destination = workspace / repo_name

    if destination.exists():
        shutil.rmtree(destination)

    Repo.clone_from(
        repo_url,
        destination
    )

    return destination