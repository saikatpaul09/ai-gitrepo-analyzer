import asyncio

from app.agents.architecture_agent import ArchitectureAgent
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

    architecture_agent = ArchitectureAgent(
        llm_client=llm_client,
    )

    # --------------------------------------------
    # Repository
    # --------------------------------------------

    repository_id = (
        "saikatpaul09_E-Commerce-project"
    )

    # --------------------------------------------
    # Architecture-focused query
    # --------------------------------------------

    query = """
    Find code that reveals the application's architecture,
    including routes, controllers, services, components,
    database access, API boundaries, business logic,
    module responsibilities, and dependencies between
    different parts of the application.
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
        f"\nRetrieved {len(results)} architecture-relevant chunks"
    )

    if not results:
        print("No relevant chunks found.")
        return

    # --------------------------------------------
    # Analyze
    # --------------------------------------------

    analysis = await architecture_agent.analyze(
        repository_context=results,
    )

    # --------------------------------------------
    # Display findings
    # --------------------------------------------

    print("\n")
    print("=" * 60)
    print("ARCHITECTURE ANALYSIS")
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