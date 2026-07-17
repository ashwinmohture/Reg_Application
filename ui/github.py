import streamlit as st

from services.github_service import clone_repository


def show_github_import(workspace):

    st.subheader("🌐 GitHub Repository")

    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/user/repository"
    )

    if st.button(
        "Clone Repository",
        use_container_width=True
    ):

        if not repo_url:

            st.warning(
                "Please enter a repository URL."
            )

            return

        with st.spinner(
            "Cloning repository..."
        ):

            path = clone_repository(
                repo_url,
                workspace
            )

        st.success(
            f"Repository cloned to\n\n{path}"
        )

        return path