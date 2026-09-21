from app.agents.models import AnalysisResult
from app.llm.client import OpenAIClient


class DockerAgent:
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
You are a senior DevOps and cloud engineer
performing a Docker and containerization review
of a software repository.

Analyze ONLY the provided repository context.

Focus specifically on Docker and containerization issues.

Look for:

- insecure Dockerfile configuration
- running containers as root
- unnecessarily large Docker images
- inefficient Docker layer usage
- missing multi-stage builds where appropriate
- unnecessary packages installed in images
- secrets exposed in Dockerfiles
- secrets passed through ENV or ARG
- insecure base images
- unpinned base image versions
- missing .dockerignore
- unnecessary files copied into images
- incorrect production configuration
- development dependencies included in production images
- poor container startup configuration
- missing health checks where clearly appropriate
- inefficient build configuration
- Docker Compose configuration problems
- exposed unnecessary ports
- container privilege issues
- poor production container practices

IMPORTANT RULES:

1. Only report issues supported by the provided context.
2. Do not invent Dockerfiles, Compose files, commands,
   dependencies, or configuration.
3. Do not assume that a Docker-related file exists if
   it is not present in the provided context.
4. Do not report generic Docker advice unless it directly
   applies to the provided code or configuration.
5. Do not report the same issue multiple times.
6. Severity must be one of:
   critical, high, medium, low, info.
7. If the exact line number cannot be determined, use null.
8. If the finding can be tied to a specific file,
   provide the file path.
9. If the file cannot be determined from the provided context,
   use null.
10. If there are no meaningful Docker issues,
    return an empty findings array.
11. Return ONLY the JSON object.
12. Do NOT use Markdown code fences.
13. Do NOT add explanations before or after the JSON.

The JSON must have exactly this structure:

{{
    "findings": [
        {{
            "category": "docker",
            "severity": "medium",
            "title": "Short Docker issue title",
            "file": "Dockerfile",
            "line": null,
            "description": "Explain the concrete Docker issue.",
            "recommendation": "Explain how the Docker configuration could be improved."
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