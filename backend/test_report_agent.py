import asyncio

from app.agents.critic_agent import CriticAgent
from app.agents.orchestrator import AnalysisOrchestrator
from app.agents.report_agent import ReportAgent
from app.llm.client import OpenAIClient


async def main():

    repository_id = (
        "saikatpaul09_E-Commerce-project"
    )

    print("=" * 60)
    print("AI ENGINEERING ANALYZER")
    print("=" * 60)

    # -----------------------------------------
    # 1. Run specialist agents
    # -----------------------------------------

    print("\nRunning specialist agents...")

    orchestrator = AnalysisOrchestrator()

    findings = await orchestrator.analyze(
        repository_id=repository_id,
    )

    print(
        f"\nRaw findings: {len(findings)}"
    )

    if not findings:
        print("No findings generated.")
        return

    # -----------------------------------------
    # 2. Run Critic
    # -----------------------------------------

    print("\nRunning Critic Agent...")

    llm_client = OpenAIClient()

    critic = CriticAgent(
        llm_client=llm_client,
    )

    validated_result = await critic.analyze(
        findings=findings,
    )

    validated_findings = (
        validated_result.findings
    )

    print(
        f"Validated findings: "
        f"{len(validated_findings)}"
    )

    # -----------------------------------------
    # 3. Run Report Agent
    # -----------------------------------------

    print("\nRunning Report Agent...")

    report_agent = ReportAgent(
        llm_client=llm_client,
    )

    report = await report_agent.generate_report(
        findings=validated_findings,
    )

    # -----------------------------------------
    # 4. Display report
    # -----------------------------------------

    print("\n")
    print("=" * 60)
    print("FINAL ENGINEERING REPORT")
    print("=" * 60)

    print("\nSUMMARY")
    print("-" * 60)

    print(
        f"Total findings: "
        f"{report.summary.total_findings}"
    )

    print(
        f"Critical: "
        f"{report.summary.critical}"
    )

    print(
        f"High: "
        f"{report.summary.high}"
    )

    print(
        f"Medium: "
        f"{report.summary.medium}"
    )

    print(
        f"Low: "
        f"{report.summary.low}"
    )

    print(
        f"Info: "
        f"{report.summary.info}"
    )

    print("\nEXECUTIVE SUMMARY")
    print("-" * 60)

    print(report.executive_summary)

    print("\nFINDINGS")
    print("-" * 60)

    for index, finding in enumerate(
        report.findings,
        start=1,
    ):
        print(
            f"\n--- Finding {index} ---"
        )

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
            f"Description: "
            f"{finding.description}"
        )

        print(
            f"Recommendation: "
            f"{finding.recommendation}"
        )

    print("\nRECOMMENDATIONS")
    print("-" * 60)

    for index, recommendation in enumerate(
        report.recommendations,
        start=1,
    ):
        print(
            f"{index}. {recommendation}"
        )


if __name__ == "__main__":
    asyncio.run(main())