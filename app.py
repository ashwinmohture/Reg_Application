import sys
from pathlib import Path


class _PipeSafeStream:
    """
    Wraps a stream (stdout/stderr) so that write() never raises.

    On Windows, Streamlit's dev-mode rerun / file watcher can tear down
    the console pipe attached to a running script (most likely to happen
    while a script run is mid-flight on a slow blocking call, e.g. an
    embedding/LLM API request). Any subsequent print()/log write - ours
    or a third-party library's - then raises:

        OSError: [WinError 233] No process is on the other end of the pipe

    which crashes the whole request even though it has nothing to do
    with the actual logic that was running. This wrapper swallows that
    specific failure mode instead of letting it propagate.
    """

    def __init__(self, stream):
        self._stream = stream

    def write(self, data):
        try:
            return self._stream.write(data)
        except OSError:
            return 0

    def flush(self):
        try:
            self._stream.flush()
        except OSError:
            pass

    def __getattr__(self, name):
        return getattr(self._stream, name)


if sys.platform == "win32":
    sys.stdout = _PipeSafeStream(sys.stdout)
    sys.stderr = _PipeSafeStream(sys.stderr)


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
from ui.settings import show_settings

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
    "Intelligent Codebase Knowledge & Review Assistant"
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

elif page == "⚙ Settings":

    show_settings()

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

    else:

        st.info(
            "📦 Please upload and index a project to start using CodePilot AI."
        )