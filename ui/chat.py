import streamlit as st

from rag.rag_chain import ask_codebase


def show_chat(retriever):

    st.subheader("💬 Ask Your Codebase")

    # ==============================
    # Display Chat History
    # ==============================

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if message["role"] == "assistant":

                sources = message.get("sources", [])

                if sources:

                    st.markdown("### 📚 Sources Used")

                    for source in sources:

                        with st.expander(f"📄 {source['source']}"):

                            st.code(
                                source["content"],
                                language=source["language"]
                            )

    # ==============================
    # Chat Input
    # ==============================

    question = st.chat_input(
        "Ask anything about your project..."
    )

    if not question:
        return

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Searching codebase..."):

            result = ask_codebase(
                retriever,
                question
            )

            answer = result["answer"]

            st.markdown(answer)

            sources = []

            source_names = set()

            language_map = {
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
                ".yaml": "yaml"
            }

            for doc in result["sources"]:

                source = doc.metadata.get("source")

                extension = doc.metadata.get(
                    "extension",
                    ""
                )

                if source in source_names:
                    continue

                source_names.add(source)

                sources.append({
                    "source": source,
                    "content": doc.page_content,
                    "language": language_map.get(
                        extension,
                        "text"
                    )
                })

            if sources:

                st.markdown("### 📚 Sources Used")

                for source in sources:

                    with st.expander(
                        f"📄 {source['source']}"
                    ):

                        st.code(
                            source["content"],
                            language=source["language"]
                        )

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })