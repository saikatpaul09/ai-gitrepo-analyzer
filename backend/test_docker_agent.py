import asyncio

from app.agents.docker_agent import DockerAgent
from app.llm.client import OpenAIClient
from app.rag.embeddings import EmbeddingService
from app.rag.qdrant import QdrantService
from app.rag.retriever import RepositoryRetriever


async def main():
    print("Starting Docker Agent test...")

    embedding_service = EmbeddingService()
    qdrant_service = QdrantService()

    retriever = RepositoryRetriever(
        embedding_service=embedding_service,
        qdrant_service=qdrant_service,
    )

    llm_client = OpenAIClient()

    docker_agent = DockerAgent(
        llm_client=llm_client,
    )

    repository_id = "saikatpaul09_E-Commerce-project"

    query = """
    Find Dockerfiles, docker-compose files,
    container configuration, Docker build configuration,
    base images, exposed ports, environment variables,
    container commands, health checks, production
    configuration, and container dependencies.
    """

    print("Retrieving Docker-related repository context...")

    results = retriever.retrieve(
        query=query,
        repository_id=repository_id,
        limit=8,
    )

    print(
        f"Retrieved {len(results)} Docker-related chunks"
    )

    if not results:
        print("No relevant chunks found.")
        return

    print("Running Docker Agent...")

    analysis = await docker_agent.analyze(
        repository_context=results,
    )

    print("\n")
    print("=" * 60)
    print("DOCKER ANALYSIS")
    print("=" * 60)

    print(
        f"\nFindings: {len(analysis.findings)}\n"
    )

    for index, finding in enumerate(
        analysis.findings,
        start=1,
    ):
        print(f"--- Finding {index} ---")
        print(f"Category: {finding.category}")
        print(f"Severity: {finding.severity}")
        print(f"Title: {finding.title}")
        print(f"File: {finding.file}")
        print(f"Line: {finding.line}")
        print(f"Description: {finding.description}")
        print(f"Recommendation: {finding.recommendation}")
        print()


if __name__ == "__main__":
    asyncio.run(main())