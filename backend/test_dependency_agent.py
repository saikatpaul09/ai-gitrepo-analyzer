import asyncio

from app.agents.dependency_agent import DependencyAgent
from app.llm.client import OpenAIClient
from app.rag.embeddings import EmbeddingService
from app.rag.qdrant import QdrantService
from app.rag.retriever import RepositoryRetriever


async def main():

    # --------------------------------------------
    # Initialize RAG
    # --------------------------------------------

    embedding_service = EmbeddingService()

    qdrant_service = QdrantService()

    retriever = RepositoryRetriever(
        embedding_service=embedding_service,
        qdrant_service=qdrant_service,
    )

    # --------------------------------------------
    # Initialize LLM
    # --------------------------------------------

    llm_client = OpenAIClient()

    dependency_agent = DependencyAgent(
        llm_client=llm_client,
    )

    # --------------------------------------------
    # Repository
    # --------------------------------------------

    repository_id = (
        "saikatpaul09_E-Commerce-project"
    )

    # --------------------------------------------
    # Dependency-focused query
    # --------------------------------------------

    query = """
    Find package manifests, dependency configuration,
    lockfiles, package manager configuration, Docker
    dependencies, runtime dependencies, development
    dependencies, and version declarations.
    """

    # --------------------------------------------
    # Retrieve relevant code
    # --------------------------------------------

    results = retriever.retrieve(
        query=query,
        repository_id=repository_id,
        limit=8,
    )

    print(
        f"\nRetrieved {len(results)} dependency-relevant chunks"
    )

    if not results:
        print("No relevant chunks found.")
        return

    # --------------------------------------------
    # Analyze
    # --------------------------------------------

    analysis = await dependency_agent.analyze(
        repository_context=results,
    )

    # --------------------------------------------
    # Display findings
    # --------------------------------------------

    print("\n")
    print("=" * 60)
    print("DEPENDENCY ANALYSIS")
    print("=" * 60)

    print(
        f"\nFindings: {len(analysis.findings)}\n"
    )

    for index, finding in enumerate(
        analysis.findings,
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
            f"Recommendation: {finding.recommendation}"
        )

        print()


if __name__ == "__main__":
    asyncio.run(main())