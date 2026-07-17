import streamlit as st

from services.search_service import semantic_search
from ui.file_actions import show_file_actions


LANGUAGE_MAP = {
    ".py": "python",
    ".php": "php",
    ".java": "java",
    ".js": "javascript",
    ".ts": "typescript",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
    ".xml": "xml",
    ".json": "json",
    ".yml": "yaml",
    ".yaml": "yaml",
}


def show_search(retriever):

    st.subheader("🔍 Semantic Code Search")

    query = st.text_input(
        "Search by functionality",
        placeholder="authentication, login, inventory..."
    )

    if not query:
        return

    with st.spinner("Searching repository..."):

        docs = semantic_search(
            retriever,
            query
        )

    if not docs:

        st.warning("No matching files found.")

        return

    shown = set()

    for doc in docs:

        source = doc.metadata.get("source")

        if source in shown:
            continue

        shown.add(source)

        extension = doc.metadata.get(
            "extension",
            ""
        )

        language = LANGUAGE_MAP.get(
            extension,
            "text"
        )

        with st.expander(f"📄 {source}"):

            st.code(
                doc.page_content,
                language=language
            )

        show_file_actions(
            st.session_state.llm,
            source,
            doc.page_content
        )    