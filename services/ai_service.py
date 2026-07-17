from services.ask_file import ask_file


def explain_code(model, code):

    return ask_file(
        model,
        "Explain this code in detail. Include purpose, workflow, important methods, and dependencies.",
        code
    )


def find_bugs(model, code):

    return ask_file(
        model,
        """Analyze this code and identify:

1. Bugs
2. Security vulnerabilities
3. Code smells
4. Performance issues
5. Suggested fixes""",
        code
    )


def optimize_code(model, code):

    return ask_file(
        model,
        """Optimize this code.

Improve:
- Readability
- Performance
- Maintainability

Explain every improvement.""",
        code
    )


def generate_tests(model, code):

    return ask_file(
        model,
        "Generate comprehensive unit tests for this code.",
        code
    )


def generate_docs(model, code):

    return ask_file(
        model,
        """Generate professional documentation.

Include:
- Purpose
- Classes
- Methods
- Parameters
- Return Values
- Example Usage""",
        code
    )