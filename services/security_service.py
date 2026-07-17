from rag.ask_file import ask_file


def scan_security(model, code):

    prompt = """
You are a Senior Application Security Engineer.

Analyze the following code and identify:

1. SQL Injection
2. Cross Site Scripting (XSS)
3. Hardcoded Secrets
4. Weak Authentication
5. Missing Validation
6. Sensitive Information Exposure
7. Code Smells
8. Performance Problems

For each issue provide:

- Severity (High / Medium / Low)
- Issue
- Explanation
- Recommendation

If no issues are found, say:
"No major security issues found."
"""

    return ask_file(
        model,
        prompt,
        code
    )