import streamlit as st

from services.security_service import scan_security


def show_security(retriever):

    st.subheader("🛡 Security Scanner")

    st.write(
        "Analyze your repository for security vulnerabilities."
    )

    if st.button(
        "🚀 Scan Repository",
        use_container_width=True
    ):

        with st.spinner("Scanning..."):

            docs = retriever.invoke(
                "security vulnerabilities"
            )

            report = ""

            for doc in docs:

                source = doc.metadata.get(
                    "source",
                    "Unknown"
                )

                report += f"\n\n## 📄 {source}\n\n"

                result = scan_security(
                    st.session_state.llm,
                    doc.page_content
                )

                if result:
                    report += result
                else:
                    report += "No security report generated."

                    st.success("Security Scan Completed")

        st.markdown(report)