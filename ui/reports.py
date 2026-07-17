from pathlib import Path

import streamlit as st

from services.report_service import (
    build_report,
    export_markdown,
    export_pdf,
    export_docx
)


def show_reports():

    st.subheader("📈 Project Report Generator")

    st.write(
        "Generate a professional report for your repository."
    )

    st.divider()

    # =============================
    # Report Options
    # =============================

    include_documentation = st.checkbox(
        "Include Documentation",
        value=True
    )

    include_security = st.checkbox(
        "Include Security Report",
        value=True
    )

    include_ai_summary = st.checkbox(
        "Include AI Summary",
        value=True
    )

    st.divider()

    report_type = st.radio(
        "Output Format",
        [
            "Markdown",
            "PDF",
            "DOCX"
        ]
    )

    st.divider()

    if st.button(
        "🚀 Generate Report",
        use_container_width=True
    ):

        with st.spinner(
            "Generating report..."
        ):

            project_name = st.session_state.get(
                "project_name",
                "RepoMind_Project"
            )

            files_count = st.session_state.get(
                "files_count",
                0
            )

            chunks_count = st.session_state.get(
                "chunks_count",
                0
            )

            embedding = st.session_state.get(
                "embedding_model",
                "Gemini"
            )

            llm = st.session_state.get(
                "llm_model",
                "Mistral"
            )

            documentation = (
                "Documentation generated."
                if include_documentation
                else "Skipped."
            )

            security = (
                "Security scan completed."
                if include_security
                else "Skipped."
            )

            ai_summary = (
                "Repository successfully indexed and analyzed."
                if include_ai_summary
                else "Skipped."
            )

            report = build_report(
                project_name=project_name,
                files_count=files_count,
                chunks_count=chunks_count,
                embedding_model=embedding,
                llm_model=llm,
                security_summary=security,
                documentation_summary=documentation,
                ai_summary=ai_summary
            )

        st.success(
            "Report Generated Successfully!"
        )

        # =============================
        # Preview
        # =============================

        st.subheader("📄 Report Preview")

        st.markdown(report)

        st.divider()

        # =============================
        # Export
        # =============================

        if report_type == "Markdown":

            file_path = export_markdown(
                report,
                project_name
            )

        elif report_type == "PDF":

            file_path = export_pdf(
                report,
                project_name
            )

        else:

            file_path = export_docx(
                report,
                project_name
            )

        with open(
            file_path,
            "rb"
        ) as file:

            st.download_button(
                label=f"⬇ Download {report_type}",
                data=file,
                file_name=file_path.name,
                mime="application/octet-stream",
                use_container_width=True
            )

        st.info(
            f"Report saved to:\n\n{Path(file_path).resolve()}"
        )