import streamlit as st

from services.ai_service import ask_file


def show_file_actions(model, source, code):

    st.divider()
    st.subheader("🤖 AI File Actions")

    col1, col2, col3, col4, col5 = st.columns(5)

    explain = col1.button(
        "🚀 Explain",
        key=f"explain_{source}"
    )

    bugs = col2.button(
        "🐞 Find Bugs",
        key=f"bugs_{source}"
    )

    optimize = col3.button(
        "⚡ Optimize",
        key=f"optimize_{source}"
    )

    document = col4.button(
        "📝 Generate Docs",
        key=f"docs_{source}"
    )

    tests = col5.button(
        "🧪 Generate Tests",
        key=f"tests_{source}"
    )

    if explain:
        with st.spinner("Analyzing code..."):
            answer = ask_file(
                model,
                "Explain this code in detail. Describe its purpose, architecture, important functions, and execution flow.",
                code
            )
        st.success(answer)

    if bugs:
        with st.spinner("Finding bugs..."):
            answer = ask_file(
                model,
                "Review this code. Find bugs, logical issues, security vulnerabilities, performance problems, and code smells.",
                code
            )
        st.warning(answer)

    if optimize:
        with st.spinner("Optimizing code..."):
            answer = ask_file(
                model,
                "Optimize this code. Suggest better algorithms, cleaner architecture, improved readability, and performance enhancements.",
                code
            )
        st.info(answer)

    if document:
        with st.spinner("Generating documentation..."):
            answer = ask_file(
                model,
                "Generate professional documentation for this file, including purpose, classes, functions, parameters, return values, and usage examples.",
                code
            )
        st.success(answer)

    if tests:
        with st.spinner("Generating unit tests..."):
            answer = ask_file(
                model,
                "Generate comprehensive unit tests for this code. Include edge cases and explain the test scenarios.",
                code
            )
        st.code(answer, language="python")