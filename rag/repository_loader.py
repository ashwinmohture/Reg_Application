from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".py", ".php", ".java", ".js", ".ts",
    ".sql", ".html", ".twig", ".css"
}

def load_repository(project_path):
    documents = []
    project_path = Path(project_path)

    for file_path in project_path.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            documents.append({
                "content": content,
                "source": str(
                    file_path.relative_to(project_path)
                ),
                "extension": file_path.suffix
            })
        except Exception as error:
            print(f"Failed to load {file_path}: {error}")

    return documents
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py",
    ".php",
    ".java",
    ".js",
    ".ts",
    ".sql",
    ".html",
    ".twig",
    ".css"
}


def load_repository(project_path):

    documents = []

    project_path = Path(project_path)


    for file_path in project_path.rglob("*"):

        if not file_path.is_file():
            continue

        if (
            file_path.suffix.lower()
            not in SUPPORTED_EXTENSIONS
        ):
            continue


        try:

            content = file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )


            relative_path = file_path.relative_to(
                project_path
            )


            documents.append({
                "content": content,
                "source": str(relative_path),
                "extension": file_path.suffix
            })


        except Exception as error:

            print(
                f"Failed to load "
                f"{file_path}: {error}"
            )


    return documents