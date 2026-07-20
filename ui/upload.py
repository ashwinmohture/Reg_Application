from pathlib import Path
import shutil
import zipfile

import streamlit as st

from services.workspace_service import (
    create_project,
    project_exists,
    get_source_path,
    update_metadata,
)

from rag.repository_loader import load_repository
from rag.code_splitter import split_code_documents
from rag.embeddings import get_embedding_model
from rag.vector_store import create_vector_store
from rag.retriever import create_retriever


def show_upload(upload_dir, extract_dir):

    st.subheader("📦 Upload Project")

    uploaded_file = st.file_uploader(
        "Upload your project ZIP file",
        type=["zip"],
        key="project_upload"
    )

    if uploaded_file is None:
        return

    project_name = st.text_input(
        "Project Name",
        value=Path(uploaded_file.name).stem.replace(" ", "_"),
        key="upload_project_name"
    )

    if not project_name.strip():
        st.warning("Please enter a project name.")
        return

    if not st.button(
        "🚀 Index Codebase",
        use_container_width=True
    ):
        return

    with st.spinner("Analyzing and indexing codebase..."):

        try:

            project_name = project_name.strip().replace(" ", "_")

            # Create project if it doesn't exist
            if not project_exists(project_name):
                create_project(project_name)

            # Source folder
            extract_dir = get_source_path(project_name)

            if extract_dir.exists():
                shutil.rmtree(extract_dir)

            extract_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            # Save uploaded ZIP
            zip_path = upload_dir / uploaded_file.name

            with open(zip_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Extract ZIP
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            # Load repository
            documents = load_repository(extract_dir)

            if not documents:
                st.error("No supported code files found.")
                return

            # Split documents
            chunks = split_code_documents(documents)

            # Embeddings - throttled to stay under the provider's
            # rate limit, so large projects don't hit 429
            # RESOURCE_EXHAUSTED. embed_documents() runs during
            # create_vector_store() below and can take a while for
            # big codebases, so show real progress instead of a
            # frozen spinner.
            progress_bar = st.progress(
                0,
                text="Preparing to embed code chunks..."
            )

            def _on_embed_progress(done, total):

                progress_bar.progress(
                    done / total,
                    text=f"Embedding chunks... {done}/{total}"
                )

            embedding_model = get_embedding_model(
                progress_callback=_on_embed_progress
            )

            # Release previous retriever / vector store references so the
            # old chroma.sqlite3 file handle isn't still open when we try
            # to delete it in create_vector_store()
            st.session_state.retriever = None
            st.session_state.pop("vector_store", None)

            # Create vector database
            vector_store = create_vector_store(
                chunks,
                embedding_model,
                project_name
            )

            retriever = create_retriever(
                vector_store
            )

            progress_bar.empty()

            files = len(documents)
            chunk_count = len(chunks)

            # Session State
            st.session_state.retriever = retriever
            st.session_state.files_count = files
            st.session_state.chunks_count = chunk_count
            st.session_state.current_project = project_name
            st.session_state.active_project = project_name
            st.session_state.project_name = project_name
            st.session_state.messages = []

            # Metadata
            update_metadata(
                project_name=project_name,
                files=files,
                chunks=chunk_count,
                embedding="Gemini",
                llm="Mistral"
            )

            st.success("✅ Repository Indexed Successfully")

        except Exception as error:

            st.exception(error)