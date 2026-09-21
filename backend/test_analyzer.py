import asyncio

from app.agents.engineering_analyzer import EngineeringAnalyzer
from app.llm.client import OpenAIClient
from app.rag.embeddings import EmbeddingService
from app.rag.qdrant import QdrantService
from app.rag.retriever import RepositoryRetriever


async def main():

    # --------------------------------------------
    # Initialize RAG services
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

    analyzer = EngineeringAnalyzer(
        llm_client=llm_client,
    )

    # --------------------------------------------
    # Repository
    # --------------------------------------------

    repository_id = (
        "saikatpaul09_E-Commerce-project"
    )

    # --------------------------------------------
    # Query
    # --------------------------------------------

    query = (
        "Analyze the authentication and login implementation "
        "for security, architecture, and error handling issues."
    )

    # --------------------------------------------
    # Retrieve relevant code
    # --------------------------------------------

    results = retriever.retrieve(
        query=query,
        repository_id=repository_id,
        limit=5,
    )

    print(
        f"\nRetrieved {len(results)} chunks"
    )

    if not results:
        print("No relevant chunks found.")
        return

    # --------------------------------------------
    # Analyze
    # --------------------------------------------

    analysis = await analyzer.analyze(
        repository_context=results,
    )

    # --------------------------------------------
    # Display structured findings
    # --------------------------------------------

    print("\n")
    print("=" * 60)
    print("AI ENGINEERING ANALYSIS")
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