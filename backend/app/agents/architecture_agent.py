from app.agents.models import AnalysisResult
from app.llm.client import OpenAIClient


class ArchitectureAgent:
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
You are a senior software architect reviewing
a software repository.

Analyze ONLY the provided repository code.

Focus specifically on architectural and
design-quality issues.

Look for:

- poor separation of responsibilities
- tightly coupled modules
- inappropriate business logic placement
- duplicated responsibilities
- poor API/service boundaries
- problematic dependency direction
- circular dependency risks
- poor abstraction
- inappropriate global state
- scalability concerns
- poor error-handling architecture
- database access architecture problems
- inconsistent architectural patterns
- maintainability problems
- violations of common software design principles

IMPORTANT RULES:

1. Only report issues supported by the provided code.
2. Do not invent files, functions, dependencies, or behavior.
3. Do not assume the entire architecture from a small
   portion of the repository.
4. Avoid generic software-development advice unless it
   directly applies to the provided code.
5. Do not report the same issue multiple times.
6. Severity must be one of:
   critical, high, medium, low, info.
7. If the exact line number cannot be determined, use null.
8. If the finding can be tied to a specific file,
   provide the file path.
9. If the file cannot be determined from the provided context,
   use null.
10. If there are no meaningful architectural issues,
    return an empty findings array.
11. Return ONLY the JSON object.
12. Do NOT use Markdown code fences.
13. Do NOT add explanations before or after the JSON.

The JSON must have exactly this structure:

{{
    "findings": [
        {{
            "category": "architecture",
            "severity": "medium",
            "title": "Short architectural issue title",
            "file": "path/to/file.py",
            "line": null,
            "description": "Explain the concrete architectural issue.",
            "recommendation": "Explain how the architecture could be improved."
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