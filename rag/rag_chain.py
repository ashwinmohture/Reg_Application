import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)


def ask_codebase(retriever, question):

    api_key = os.getenv("MISTRALAI_API_KEY")

    if not api_key:
        raise ValueError(
            f"MISTRALAI_API_KEY not found in {ENV_PATH}"
        )

    # Retrieve relevant code
    documents = retriever.invoke(question)

    # Create context
    context = "\n\n".join(
        [
            f"""
SOURCE: {doc.metadata.get("source")}

CODE:
{doc.page_content}
"""
            for doc in documents
        ]
    )

    # Create prompt
    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are RepoMind AI, an intelligent codebase assistant.

Answer using ONLY the provided code context.

If the answer cannot be found, say:
"I could not find this information in the indexed codebase."

Explain the code clearly.

CODE CONTEXT:

{context}
"""
        ),
        (
            "human",
            "{question}"
        )
    ])

    model = ChatMistralAI(
        model="mistral-large-latest",
        api_key=api_key,
        temperature=0.2
    )

    prompt = prompt_template.format_messages(
        context=context,
        question=question
    )

    result = model.invoke(prompt)

    return {
        "answer": result.content,
        "sources": documents
    }