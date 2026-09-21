from app.agents.models import AnalysisResult
from app.llm.client import OpenAIClient


class DependencyAgent:
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

Content:
{result["content"]}
"""
            )

        context = "\n".join(context_parts)

        prompt = f"""
You are a senior software engineer specializing
in dependency management and software supply-chain security.

Analyze ONLY the provided repository context.

Focus specifically on dependency-related issues.

Look for:

- suspicious dependencies
- unnecessary dependencies
- duplicate dependencies
- dependency version inconsistencies
- potentially outdated dependency versions
- insecure dependency usage
- excessive dependency usage
- development dependencies incorrectly used in production
- missing dependency version constraints
- dependency management inconsistencies
- package manager configuration problems
- lockfile inconsistencies
- dependency-related supply-chain risks

IMPORTANT RULES:

1. Only report issues supported by the provided context.
2. Do not invent dependencies or versions.
3. Do not claim a dependency has a known vulnerability unless
   the provided context gives sufficient evidence.
4. Do not claim a package is outdated unless the provided
   context gives enough information to support that conclusion.
5. Do not report the same issue multiple times.
6. Severity must be one of:
   critical, high, medium, low, info.
7. If the exact line number cannot be determined, use null.
8. If the finding can be tied to a specific file,
   provide the file path.
9. If the file cannot be determined from the provided context,
   use null.
10. If there are no meaningful dependency issues,
    return an empty findings array.
11. Return ONLY the JSON object.
12. Do NOT use Markdown code fences.
13. Do NOT add explanations before or after the JSON.

The JSON must have exactly this structure:

{{
    "findings": [
        {{
            "category": "dependency",
            "severity": "medium",
            "title": "Short dependency issue title",
            "file": "package.json",
            "line": null,
            "description": "Explain the concrete dependency issue.",
            "recommendation": "Explain how the dependency configuration could be improved."
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