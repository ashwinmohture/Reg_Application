from langchain_core.prompts import ChatPromptTemplate


def ask_file(model, prompt_text, code):
    """
    Sends a prompt and source code to the LLM and
    returns the generated response.
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an expert software engineer,
code reviewer and software architect.

Analyze the provided source code carefully and
respond in a clear, professional and structured format.
"""
            ),
            (
                "human",
                """
Instruction:

{instruction}

----------------------------------------

Source Code:

{code}
"""
            ),
        ]
    )

    messages = prompt.format_messages(
        instruction=prompt_text,
        code=code,
    )

    response = model.invoke(messages)

    return response.content