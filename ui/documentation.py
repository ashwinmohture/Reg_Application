import streamlit as st

from services.documentation_service import (
    generate_documentation
)


def show_documentation(retriever):

    st.subheader("📄 Documentation Generator")

    options = st.multiselect(

        "Select Documentation",

        [

            "README",

            "Summary",

            "Folder Structure",

            "API",

            "Classes",

            "Architecture",

            "Development Guide"

        ],

        default=[

            "README",

            "Summary"

        ]

    )

    if st.button(

        "🚀 Generate Documentation",

        use_container_width=True

    ):

        with st.spinner(

            "Generating documentation..."

        ):

            documentation = generate_documentation(

                st.session_state.llm,

                retriever,

                options

            )

        st.success(

            "Documentation Generated Successfully"

        )

        st.markdown(documentation)

        st.download_button(

            "⬇ Download README.md",

            documentation,

            file_name="README.md",

            mime="text/markdown"

        )