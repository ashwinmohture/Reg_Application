from pathlib import Path

import streamlit as st


LANGUAGE = {
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
}


def show_code_explorer(project_path):

    st.subheader("📂 Project Explorer")
    st.caption(
        f"Current Project : {st.session_state.current_project}"
    )

    if not project_path.exists():

        st.warning("Project not found.")

        return

    files = sorted(
        project_path.rglob("*")
    )

    code_files = [
        file
        for file in files
        if file.is_file()
    ]

    if not code_files:

        st.info("No files found.")
        return
    
    search = st.text_input(
        "🔍 Search File"
    )

    # file_names = [
    #     file.relative_to(project_path).as_posix()
    #     for file in code_files
    # ]
    file_names = []

    for file in code_files:

        relative = file.relative_to(
            project_path
        ).as_posix()

        if search:

            if search.lower() not in relative.lower():
                continue

        file_names.append(relative)

    selected = st.selectbox(
        "Repository Files",
        file_names
    )

    selected_file = (
        project_path /
        selected
    )
    size = selected_file.stat().st_size

    st.write(
        f"Size : {size} bytes"
    )

    st.write(
        f"Extension : {selected_file.suffix}"
    )

    st.caption(
        f"📄 {selected}"
    )

    extension = selected_file.suffix

    language = LANGUAGE.get(
        extension,
        "text"
    )

    with open(
        selected_file,
        encoding="utf-8",
        errors="ignore"
    ) as file:

        code = file.read()

    st.code(
        code,
        language=language
    )

    st.download_button(
        "⬇ Download File",
        data=code,
        file_name=selected_file.name,
        use_container_width=True
    )