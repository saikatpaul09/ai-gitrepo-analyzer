from app.agents.models import (
    AnalysisReport,
    Finding,
)
from app.llm.client import OpenAIClient


class ReportAgent:

    def __init__(
        self,
        llm_client: OpenAIClient,
    ):
        self.llm_client = llm_client

    async def generate_report(
        self,
        findings: list[Finding],
    ) -> AnalysisReport:

        if not findings:
            return AnalysisReport(
                summary={
                    "total_findings": 0,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "info": 0,
                },
                executive_summary=(
                    "No significant engineering issues "
                    "were identified from the analyzed "
                    "repository context."
                ),
                findings=[],
                recommendations=[],
            )

        findings_context = []

        for index, finding in enumerate(
            findings,
            start=1,
        ):
            findings_context.append(
                f"""
Finding {index}:

Category: {finding.category}
Severity: {finding.severity}
Title: {finding.title}
File: {finding.file}
Line: {finding.line}

Description:
{finding.description}

Recommendation:
{finding.recommendation}
"""
            )

        context = "\n".join(findings_context)

        prompt = f"""
You are a senior engineering lead creating
the final engineering analysis report for
a software repository.

The findings below have already been reviewed
and validated by a Critic Agent.

Your job is to create a concise and useful
engineering report.

IMPORTANT:

1. Do not create new findings.
2. Do not remove validated findings.
3. Do not change the severity of findings.
4. Do not invent files, lines, vulnerabilities,
   dependencies, or behavior.
5. Preserve the exact findings provided.
6. Create an executive summary based ONLY on
   the provided findings.
7. Create a prioritized list of recommendations
   based ONLY on the provided findings.
8. Recommendations should not introduce new issues.
9. Count every finding exactly once.
10. Severity must remain one of:
    critical, high, medium, low, info.

Return ONLY the JSON object.

Do NOT use Markdown code fences.

Do NOT add explanations before or after the JSON.

The JSON must have exactly this structure:

{{
    "summary": {{
        "total_findings": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0
    }},
    "executive_summary": "Concise overview of the repository findings.",
    "findings": [
        {{
            "category": "security",
            "severity": "high",
            "title": "Short issue title",
            "file": "path/to/file.py",
            "line": null,
            "description": "Explain the issue.",
            "recommendation": "Explain how it should be improved."
        }}
    ],
    "recommendations": [
        "Prioritized recommendation 1",
        "Prioritized recommendation 2"
    ]
}}

Validated findings:

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

        return AnalysisReport.model_validate_json(
            cleaned_response
        )