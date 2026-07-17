from langchain_chroma import Chroma

from services.workspace_service import (
    get_chroma_path
)


def create_retriever(
    vector_store
):

    return vector_store.as_retriever(
        search_kwargs={
            "k": 5
        }
    )


def load_project_retriever(
    project_name,
    embedding_model
):

    chroma_path = get_chroma_path(
        project_name
    )

    vector_store = Chroma(
        persist_directory=str(chroma_path),
        embedding_function=embedding_model,
        collection_name=project_name.strip().replace(" ", "_")
    )

    return vector_store.as_retriever(
        search_kwargs={
            "k": 5
        }
    )