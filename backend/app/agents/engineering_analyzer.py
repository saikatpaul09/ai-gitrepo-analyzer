from app.agents.models import AnalysisResult
from app.llm.client import OpenAIClient


class EngineeringAnalyzer:
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
You are a senior software engineer performing
a codebase analysis.

Analyze the provided repository code and identify
concrete engineering issues.

Look for:

- architecture problems
- security vulnerabilities
- poor error handling
- testing gaps
- maintainability problems
- performance problems
- dependency problems
- Docker or deployment problems

IMPORTANT RULES:

1. Only report issues supported by the provided code.
2. Do not invent files, functions, dependencies, or behavior.
3. If there are no meaningful issues, return an empty findings array.
4. Do not report the same issue multiple times.
5. Severity must be one of:
   critical, high, medium, low, info.
6. If the exact line number cannot be determined, use null.
7. If the finding can be tied to a specific file, provide the file path.
8. If the file cannot be determined from the provided context, use null.
9. Return ONLY the JSON object.
10. Do NOT use Markdown code fences.
11. Do NOT add explanations before or after the JSON.

The JSON must have exactly this structure:

{{
    "findings": [
        {{
            "category": "security",
            "severity": "high",
            "title": "Short issue title",
            "file": "path/to/file.py",
            "line": null,
            "description": "Explain the issue.",
            "recommendation": "Explain how it could be improved."
        }}
    ]
}}

Repository context:

{context}
"""

        raw_response = await self.llm_client.analyze(
            prompt
        )

        # Remove Markdown code fences if the model
        # returns JSON inside ```json ... ```
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