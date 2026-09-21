from app.rag.embeddings import EmbeddingService
from app.rag.qdrant import QdrantService
from app.rag.retriever import RepositoryRetriever


embedding_service = EmbeddingService()
qdrant_service = QdrantService()

retriever = RepositoryRetriever(
    embedding_service=embedding_service,
    qdrant_service=qdrant_service,
)


repository_id = "saikatpaul09_E-Commerce-project"

query = "Where is authentication or login handled?"

results = retriever.retrieve(
    query=query,
    repository_id=repository_id,
    limit=5,
)


print("\nQuery:")
print(query)

print("\nRelevant chunks:\n")

for index, result in enumerate(results, start=1):

    print(f"--- Result {index} ---")
    print("Score:", result["score"])
    print("File:", result["path"])
    print("Chunk:", result["chunk_index"])
    print("Content:")
    print(result["content"])
    print()