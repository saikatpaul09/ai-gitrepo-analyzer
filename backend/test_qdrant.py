from app.rag.embeddings import EmbeddingService
from app.rag.qdrant import QdrantService


embedding_service = EmbeddingService()

qdrant = QdrantService()

qdrant.create_collection()


chunks = [
    {
        "path": "src/auth.py",
        "content": "This file handles user authentication and login.",
        "chunk_index": 0,
    },
    {
        "path": "src/payment.py",
        "content": "This file processes credit card payments.",
        "chunk_index": 0,
    },
]


texts = [
    chunk["content"]
    for chunk in chunks
]


embeddings = embedding_service.embed(texts)


qdrant.insert_chunks(
    chunks=chunks,
    embeddings=embeddings,
)


query = "Where is user login handled?"

query_embedding = embedding_service.embed(
    [query]
)[0]


results = qdrant.search(
    query_vector=query_embedding,
    limit=2,
)


print("\nSearch results:\n")

for result in results:
    print("Score:", result.score)
    print("File:", result.payload["path"])
    print("Content:", result.payload["content"])
    print()