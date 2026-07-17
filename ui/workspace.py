import streamlit as st

from rag.embeddings import get_embedding_model
from rag.retriever import load_project_retriever

from services.workspace_service import (
    create_project,
    project_exists,
    list_projects,
    get_metadata,
)


def show_workspace():

    st.subheader("📁 Workspace")

    st.caption(
        "Manage all your indexed repositories."
    )

    st.divider()

    # ==============================
    # Create Project
    # ==============================

    st.markdown("### ➕ Create New Project")

    project_name = st.text_input(
        "Project Name",
        placeholder="Enter project name",
        key="workspace_project_name"
    )

    if st.button(
        "Create Project",
        use_container_width=True
    ):

        if not project_name.strip():

            st.warning(
                "Please enter a project name."
            )

        elif project_exists(project_name):

            st.warning(
                "Project already exists."
            )

        else:

            create_project(
                project_name.strip()
            )

            st.success(
                f"{project_name} created successfully."
            )

            st.rerun()

    st.divider()

    # ==============================
    # Existing Projects
    # ==============================

    st.markdown("### 📂 Existing Projects")

    projects = list_projects()

    if not projects:

        st.info(
            "No projects found."
        )

        return

    selected_project = st.selectbox(
        "Select Project",
        projects
    )

    metadata = get_metadata(
        selected_project
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Files",
        metadata.get(
            "files",
            0
        )
    )

    col2.metric(
        "Chunks",
        metadata.get(
            "chunks",
            0
        )
    )

    col1.metric(
        "Embedding",
        metadata.get(
            "embedding",
            "-"
        )
    )

    col2.metric(
        "LLM",
        metadata.get(
            "llm",
            "-"
        )
    )

    st.divider()

    # ==============================
    # Actions
    # ==============================

    c1, c2 = st.columns(2)

    if c1.button(
        "📂 Open Project",
        use_container_width=True
    ):

        try:

            # Load embedding model only once
            if "embedding_model" not in st.session_state:

                with st.spinner("Loading embedding model..."):

                    st.session_state.embedding_model = get_embedding_model()

            # Load retriever
            with st.spinner("Opening project..."):

                retriever = load_project_retriever(
                    selected_project,
                    st.session_state.embedding_model
                )

            # Update session
            st.session_state.retriever = retriever
            st.session_state.current_project = selected_project

            st.session_state.files_count = metadata.get(
                "files",
                0
            )

            st.session_state.chunks_count = metadata.get(
                "chunks",
                0
            )

            st.success(
                f"✅ Project '{selected_project}' opened successfully."
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Failed to open project:\n\n{e}"
            )

    if c2.button(
        "🗑 Delete Project",
        use_container_width=True
    ):

        st.info(
            "Delete functionality coming soon."
        )