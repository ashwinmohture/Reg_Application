import streamlit as st

from services.workspace_service import (
    get_metadata
)


def show_dashboard():

    project = (
        st.session_state.get("current_project")
        or
        st.session_state.get("active_project")
    )

    if not project:

        st.warning(
            "No project selected."
        )

        return

    metadata = get_metadata(project)

    st.subheader("📊 Repository Dashboard")

    st.success(
        f"📁 Current Project : {project}"
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "📄 Files",
        metadata.get("files", 0)
    )

    col2.metric(
        "🧩 Chunks",
        metadata.get("chunks", 0)
    )

    col3.metric(
        "🧠 Embedding",
        metadata.get("embedding", "-")
    )

    st.divider()

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "🤖 LLM",
        metadata.get("llm", "-")
    )

    col5.metric(
        "🛡 Security",
        metadata.get("security", "-")
    )

    col6.metric(
        "📄 Docs",
        metadata.get(
            "documentation",
            "-"
        )
    )

    st.divider()

    col7, col8 = st.columns(2)

    col7.metric(
        "📈 Reports",
        metadata.get(
            "reports",
            0
        )
    )

    col8.metric(
        "🕒 Last Indexed",
        metadata.get(
            "last_indexed",
            "-"
        )
    )