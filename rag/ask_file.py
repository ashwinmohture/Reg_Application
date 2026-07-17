from langchain_core.prompts import ChatPromptTemplate


def ask_file(model, instruction, code):
    """
    Generic helper to analyze a single source code file.
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an expert software engineer,
code reviewer,
software architect,
and security analyst.

Always provide:
- Clear explanations
- Best practices
- Professional recommendations
- Well-structured answers.
"""
            ),
            (
                "human",
                """
Task:

{instruction}

----------------------------------------

Source Code:

{code}
"""
            ),
        ]
    )

    chain = prompt | model

    response = chain.invoke(
        {
            "instruction": instruction,
            "code": code,
        }
    )

    return response.content