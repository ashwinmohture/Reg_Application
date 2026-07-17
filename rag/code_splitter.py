# Phase 2: code splitting
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_code_documents(repository_documents):

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
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = text_splitter.split_documents(
        documents
    )

    return chunks