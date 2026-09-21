from app.agents.models import AnalysisResult
from app.llm.client import OpenAIClient


class SecurityAgent:
    def __init__(
        self,
        llm_client: OpenAIClient,
    ):
        self.llm_client = llm_client

    async def analyze(
        self,
        repository_context: list[dict],
    ) -> AnalysisResult:

        context_parts = []

        for result in repository_context:
            context_parts.append(
                f"""
File: {result["path"]}
Chunk: {result["chunk_index"]}
Similarity Score: {result["score"]}

Code:
{result["content"]}
"""
            )

        context = "\n".join(context_parts)

        prompt = f"""
You are a senior application security engineer
performing a security review of a software repository.

Analyze ONLY the provided repository code.

Focus specifically on:

- authentication vulnerabilities
- authorization vulnerabilities
- broken access control
- hardcoded secrets or credentials
- API key exposure
- SQL injection
- NoSQL injection
- command injection
- cross-site scripting (XSS)
- insecure file uploads
- path traversal
- unsafe deserialization
- sensitive information exposure
- insecure password handling
- weak cryptography
- insecure token or session handling
- insecure CORS configuration
- SSRF
- missing input validation
- insecure error handling
- other concrete application security issues

IMPORTANT RULES:

1. Only report vulnerabilities supported by the provided code.
2. Do not invent files, functions, dependencies, or behavior.
3. Do not assume that a vulnerability exists merely because
   a security mechanism is not visible in the provided context.
4. Avoid generic security advice unless it relates directly
   to the provided code.
5. Do not report the same issue multiple times.
6. Severity must be one of:
   critical, high, medium, low, info.
7. If the exact line number cannot be determined, use null.
8. If the finding can be tied to a specific file,
   provide the file path.
9. If the file cannot be determined from the provided context,
   use null.
10. If there are no meaningful security issues,
    return an empty findings array.
11. Return ONLY the JSON object.
12. Do NOT use Markdown code fences.
13. Do NOT add explanations before or after the JSON.

The JSON must have exactly this structure:

{{
    "findings": [
        {{
            "category": "security",
            "severity": "high",
            "title": "Short vulnerability title",
            "file": "path/to/file.py",
            "line": null,
            "description": "Explain the concrete security issue.",
            "recommendation": "Explain how the issue could be fixed."
        }}
    ]
}}

Repository context:

{context}
"""

        raw_response = await self.llm_client.analyze(
            prompt
        )

        cleaned_response = raw_response.strip()

        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[
                len("```json"):
            ].strip()

        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[
                len("```"):
            ].strip()

        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[
                :-len("```")
            ].strip()

        return AnalysisResult.model_validate_json(
            cleaned_response
        )