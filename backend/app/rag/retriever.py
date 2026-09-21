from app.rag.embeddings import EmbeddingService
from app.rag.qdrant import QdrantService


class RepositoryRetriever:

    def __init__(
        self,
        embedding_service: EmbeddingService,
        qdrant_service: QdrantService,
    ):
        self.embedding_service = embedding_service
        self.qdrant_service = qdrant_service

    def retrieve(
        self,
        query: str,
        repository_id: str,
        limit: int = 5,
    ) -> list[dict]:

        query_embedding = self.embedding_service.embed(
            [query]
        )[0]

        results = self.qdrant_service.search(
            query_vector=query_embedding,
            repository_id=repository_id,
            limit=limit,
        )

        return [
            {
                "score": result.score,
                "path": result.payload["path"],
                "content": result.payload["content"],
                "chunk_index": result.payload["chunk_index"],
            }
            for result in results
        ]