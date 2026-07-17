# Phase 2: code splitting
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from services.settings_service import get_setting


def split_code_documents(
    repository_documents,
    chunk_size=None,
    chunk_overlap=None
):

    if chunk_size is None:
        chunk_size = get_setting("chunk_size")

    if chunk_overlap is None:
        chunk_overlap = get_setting("chunk_overlap")

    documents = []

    for item in repository_documents:

        document = Document(
            page_content=item["content"],
            metadata={
                "source": item["source"],
                "extension": item["extension"]
            }
        )

        documents.append(document)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = text_splitter.split_documents(
        documents
    )

    return chunks