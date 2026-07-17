from langchain_core.documents import Document


def semantic_search(retriever, query: str, top_k: int = 5):

    if retriever is None:
        return []

    docs = retriever.invoke(query)

    return docs[:top_k]