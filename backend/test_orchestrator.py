import asyncio

from app.agents.orchestrator import AnalysisOrchestrator


async def main():

    repository_id = (
        "saikatpaul09_E-Commerce-project"
    )

    print("=" * 60)
    print("AI ENGINEERING ANALYZER")
    print("=" * 60)

    orchestrator = AnalysisOrchestrator()

    findings = await orchestrator.analyze(
        repository_id=repository_id,
    )

    print("\n")
    print("=" * 60)
    print("COMBINED ANALYSIS")
    print("=" * 60)

    print(
        f"\nTotal findings: {len(findings)}\n"
    )

    for index, finding in enumerate(
        findings,
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