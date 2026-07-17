from pathlib import Path

import streamlit as st

from ui.sidebar import render_sidebar
from ui.upload import show_upload
from ui.dashboard import show_dashboard
from ui.explorer import show_code_explorer
from ui.chat import show_chat
from ui.search import show_search
from rag.llm import get_llm
from ui.documentation import show_documentation
from ui.github import show_github_import
from ui.security import show_security
from ui.reports import show_reports
from ui.workspace import show_workspace

# ==============================
# Configuration
# ==============================

st.set_page_config(
    page_title="CodePilot AI",
    page_icon="🚀",
    layout="wide"
)


# ==============================
# Paths
# ==============================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploaded_projects"
EXTRACT_DIR = BASE_DIR / "extracted_project"
WORKSPACE_DIR = BASE_DIR / "workspace"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

EXTRACT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

WORKSPACE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==============================
# Sidebar
# ==============================

page = render_sidebar()


# ==============================
# Session State
# ==============================

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "files_count" not in st.session_state:
    st.session_state.files_count = 0

if "chunks_count" not in st.session_state:
    st.session_state.chunks_count = 0

if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "llm" not in st.session_state:
    st.session_state.llm = get_llm()
    
if "current_project" not in st.session_state:
    st.session_state.current_project = None

if "active_project" not in st.session_state:
    st.session_state.active_project = None
    
if (
    st.session_state.current_project is None
    and st.session_state.active_project
):
    st.session_state.current_project = (
        st.session_state.active_project
    )


# ==============================
# Header
# ==============================

if st.session_state.current_project:

    st.success(
        f"Current Project : {st.session_state.current_project}"
    )

st.title("🚀 CodePilot AI")

st.caption(
    "AI-Powered Code Intelligence & Review Platform"
)

st.divider()

# ==============================
# Navigation
# ==============================

# if page == "📂 Project Manager":

#     show_upload(
#         upload_dir=UPLOAD_DIR,
#         extract_dir=EXTRACT_DIR
#     )
if page == "📁 Workspace":

    show_workspace()

elif page == "📦 Upload ZIP":

    show_upload(
        UPLOAD_DIR,
        EXTRACT_DIR
    )

elif page == "🌐 GitHub Import":

    show_github_import(
        WORKSPACE_DIR
    )
elif page == "📈 Reports":

    show_reports()

elif not st.session_state.retriever:

    st.info(
        "📦 Please upload and index a project from the Project Manager."
    )

else:

    if page == "📊 Dashboard":

        show_dashboard()

    elif page == "📂 Explorer":

        from services.workspace_service import (
            get_source_path
        )

        project = st.session_state.get("current_project")

        if project:
            show_code_explorer(
                get_source_path(project)
            )
        else:
            st.warning("No project selected.")

    elif page == "💬 AI Chat":

        show_chat(
            st.session_state.retriever
        )

    elif page == "🔍 Search":

        show_search(
            st.session_state.retriever
        )

    elif page == "📄 Documentation":

        show_documentation(
        st.session_state.retriever
    )
        
    elif page == "🛡 Security Scanner":

        show_security(
            st.session_state.retriever
        )

    elif page == "⚙ Settings":

        st.info("⚙ Settings module coming soon.")

    else:

        st.info(
            "📦 Please upload and index a project to start using RepoMind AI."
        )