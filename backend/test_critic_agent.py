import asyncio

from app.agents.critic_agent import CriticAgent
from app.agents.orchestrator import AnalysisOrchestrator
from app.llm.client import OpenAIClient


async def main():

    repository_id = (
        "saikatpaul09_E-Commerce-project"
    )

    print("=" * 60)
    print("CRITIC AGENT TEST")
    print("=" * 60)

    print("\nRunning specialist agents...")

    orchestrator = AnalysisOrchestrator()

    findings = await orchestrator.analyze(
        repository_id=repository_id,
    )

    print(
        f"\nSpecialist agents produced "
        f"{len(findings)} findings."
    )

    if not findings:
        print("No findings to review.")
        return

    print("\nRunning Critic Agent...")

    llm_client = OpenAIClient()

    critic = CriticAgent(
        llm_client=llm_client,
    )

    validated_result = await critic.analyze(
        findings=findings,
    )

    print("\n")
    print("=" * 60)
    print("VALIDATED FINDINGS")
    print("=" * 60)

    print(
        f"\nFindings after critic: "
        f"{len(validated_result.findings)}\n"
    )

    for index, finding in enumerate(
        validated_result.findings,
        start=1,
    ):
        print(f"--- Finding {index} ---")

        print(
            f"Category: {finding.category}"
        )

        print(
            f"Severity: {finding.severity}"
        )

        print(
            f"Title: {finding.title}"
        )

        print(
            f"File: {finding.file}"
        )

        print(
            f"Line: {finding.line}"
        )

        print(
            f"Description: {finding.description}"
        )

        print(
            f"Recommendation: "
            f"{finding.recommendation}"
        )

        print()


if __name__ == "__main__":
    asyncio.run(main())