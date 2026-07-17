import streamlit as st

def render_sidebar():

    with st.sidebar:

        st.title("🚀 CodePilot AI")

        page = st.radio(
            "Navigation",
            [
                "📁 Workspace",
                "📦 Upload ZIP",
                "🌐 GitHub Import",
                "📊 Dashboard",
                "📂 Explorer",
                "💬 AI Chat",
                "🔍 Search",
                "📄 Documentation",
                "🛡 Security Scanner",
                "📈 Reports",
                "⚙ Settings",
            ],
        )

    return page