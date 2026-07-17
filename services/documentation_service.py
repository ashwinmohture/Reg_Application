from langchain_core.prompts import ChatPromptTemplate


def _generate(model, context, instruction):

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert software architect."
            ),
            (
                "human",
                """
                {instruction}

                Project Code

                {context}
                """
            )
        ]
    )

    messages = prompt.format_messages(
        instruction=instruction,
        context=context
    )

    return model.invoke(messages).content


def generate_documentation(model, retriever, options):

    docs = retriever.invoke(
        "Explain the complete project"
    )

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    output = []

    if "README" in options:

        output.append(
            "# README\n\n" +
            _generate(
                model,
                context,
                "Generate a professional README.md."
            )
        )

    if "Summary" in options:

        output.append(
            "# Project Summary\n\n" +
            _generate(
                model,
                context,
                "Summarize this project."
            )
        )

    if "Architecture" in options:

        output.append(
            "# Architecture\n\n" +
            _generate(
                model,
                context,
                "Explain the project architecture."
            )
        )

    if "Classes" in options:

        output.append(
            "# Classes\n\n" +
            _generate(
                model,
                context,
                "Explain important classes and responsibilities."
            )
        )

    if "API" in options:

        output.append(
            "# API Documentation\n\n" +
            _generate(
                model,
                context,
                "Generate REST API documentation."
            )
        )

    if "Folder Structure" in options:

        output.append(
            "# Folder Structure\n\n" +
            _generate(
                model,
                context,
                "Describe the folder structure."
            )
        )

    if "Development Guide" in options:

        output.append(
            "# Development Guide\n\n" +
            _generate(
                model,
                context,
                "Write a guide for a new developer joining the project."
            )
        )

    return "\n\n---\n\n".join(output)