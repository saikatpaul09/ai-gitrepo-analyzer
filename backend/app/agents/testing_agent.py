from app.agents.models import AnalysisResult
from app.llm.client import OpenAIClient


class TestingAgent:
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
You are a senior software engineer specializing
in automated testing and software quality.

Analyze ONLY the provided repository code.

Focus specifically on testing-related issues.

Look for:

- missing unit tests
- missing integration tests
- missing API tests
- untested critical business logic
- missing authentication/authorization tests
- missing error-case tests
- missing edge-case tests
- weak assertions
- brittle tests
- excessive mocking
- poor test isolation
- duplicated test setup
- missing validation tests
- missing database tests
- missing end-to-end tests where clearly appropriate
- testability problems caused by application design

IMPORTANT RULES:

1. Only report issues supported by the provided code.
2. Do not invent tests or files that were not provided.
3. Do not claim that tests are missing from the entire
   repository unless the provided context gives sufficient
   evidence for that conclusion.
4. Distinguish between "no test was found in the provided
   context" and "the repository has no tests."
5. Avoid generic testing advice unless it directly applies
   to the provided code.
6. Do not report the same issue multiple times.
7. Severity must be one of:
   critical, high, medium, low, info.
8. If the exact line number cannot be determined, use null.
9. If the finding can be tied to a specific file,
   provide the file path.
10. If the file cannot be determined from the provided context,
    use null.
11. If there are no meaningful testing issues,
    return an empty findings array.
12. Return ONLY the JSON object.
13. Do NOT use Markdown code fences.
14. Do NOT add explanations before or after the JSON.

The JSON must have exactly this structure:

{{
    "findings": [
        {{
            "category": "testing",
            "severity": "medium",
            "title": "Short testing issue title",
            "file": "path/to/file.py",
            "line": null,
            "description": "Explain the concrete testing issue.",
            "recommendation": "Explain what test should be added or improved."
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