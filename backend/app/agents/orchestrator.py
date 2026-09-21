import asyncio

from app.agents.architecture_agent import ArchitectureAgent
from app.agents.critic_agent import CriticAgent
from app.agents.dependency_agent import DependencyAgent
from app.agents.docker_agent import DockerAgent
from app.agents.models import (
    AnalysisReport,
    AnalysisResult,
    Finding,
)
from app.agents.report_agent import ReportAgent
from app.agents.security_agent import SecurityAgent
from app.agents.testing_agent import TestingAgent
from app.llm.client import OpenAIClient
from app.rag.retriever import RepositoryRetriever


class AnalysisOrchestrator:

    def __init__(
        self,
        retriever: RepositoryRetriever,
        llm_client: OpenAIClient,
    ):

        self.retriever = retriever

        self.agents = {
            "security": SecurityAgent(
                llm_client=llm_client,
            ),
            "architecture": ArchitectureAgent(
                llm_client=llm_client,
            ),
            "testing": TestingAgent(
                llm_client=llm_client,
            ),
            "dependency": DependencyAgent(
                llm_client=llm_client,
            ),
            "docker": DockerAgent(
                llm_client=llm_client,
            ),
        }

        self.critic = CriticAgent(
            llm_client=llm_client,
        )

        self.report_agent = ReportAgent(
            llm_client=llm_client,
        )

        self.queries = {
            "security": """
            Find authentication, authorization, access control,
            passwords, tokens, secrets, API keys, user input,
            database queries, file uploads, HTTP requests,
            CORS configuration, command execution, and
            security-sensitive application code.
            """,

            "architecture": """
            Find application architecture, modules, services,
            controllers, routes, business logic, database access,
            shared utilities, application boundaries, dependency
            relationships, and major design patterns.
            """,

            "testing": """
            Find unit tests, integration tests, API tests,
            end-to-end tests, test configuration, test utilities,
            mocking, assertions, and application code that
            appears to contain important business logic.
            """,

            "dependency": """
            Find package manifests, dependency configuration,
            lockfiles, package manager configuration, runtime
            dependencies, development dependencies, dependency
            versions, and package configuration.
            """,

            "docker": """
            Find Dockerfiles, docker-compose files, container
            configuration, base images, exposed ports,
            environment variables, Docker commands, health
            checks, production container configuration,
            and container dependencies.
            """,
        }

    async def _retrieve_context(
        self,
        agent_name: str,
        repository_id: str,
    ) -> list[dict]:

        query = self.queries[agent_name]

        return await asyncio.to_thread(
            self.retriever.retrieve,
            query=query,
            repository_id=repository_id,
            limit=8,
        )

    async def _run_agent(
        self,
        agent_name: str,
        repository_id: str,
    ) -> AnalysisResult:

        agent = self.agents[agent_name]

        print(
            f"[{agent_name}] "
            f"Retrieving repository context..."
        )

        context = await self._retrieve_context(
            agent_name=agent_name,
            repository_id=repository_id,
        )

        print(
            f"[{agent_name}] "
            f"Retrieved {len(context)} chunks"
        )

        if not context:
            return AnalysisResult(
                findings=[]
            )

        print(
            f"[{agent_name}] Running agent..."
        )

        result = await agent.analyze(
            repository_context=context,
        )

        print(
            f"[{agent_name}] "
            f"Found {len(result.findings)} findings"
        )

        return result

    async def analyze(
        self,
        repository_id: str,
    ) -> AnalysisReport:

        agent_names = list(
            self.agents.keys()
        )

        print(
            f"\nStarting analysis for: "
            f"{repository_id}\n"
        )

        # -----------------------------------------
        # Specialist agents
        # -----------------------------------------

        results = await asyncio.gather(
            *[
                self._run_agent(
                    agent_name=agent_name,
                    repository_id=repository_id,
                )
                for agent_name in agent_names
            ]
        )

        findings: list[Finding] = []

        for result in results:
            findings.extend(
                result.findings
            )

        print(
            f"\nTotal findings before critic: "
            f"{len(findings)}"
        )

        # -----------------------------------------
        # Critic
        # -----------------------------------------

        print("Running Critic Agent...")

        validated_result = (
            await self.critic.analyze(
                findings=findings,
            )
        )

        validated_findings = (
            validated_result.findings
        )

        print(
            f"Findings after critic: "
            f"{len(validated_findings)}"
        )

        # -----------------------------------------
        # Report
        # -----------------------------------------

        print("Running Report Agent...")

        report = (
            await self.report_agent.generate_report(
                findings=validated_findings,
            )
        )

        print(
            "Final engineering report generated."
        )

        return report