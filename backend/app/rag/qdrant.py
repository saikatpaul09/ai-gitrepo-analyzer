import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)


class QdrantService:
    COLLECTION_NAME = "repository_chunks"
    VECTOR_SIZE = 384

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
    ):
        self.client = QdrantClient(
            host=host,
            port=port,
        )

    def create_collection(self):
        """
        Create the Qdrant collection if it does not already exist.
        """

        collections = self.client.get_collections()

        collection_names = [
            collection.name
            for collection in collections.collections
        ]

        if self.COLLECTION_NAME in collection_names:
            return

        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=VectorParams(
                size=self.VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

    def insert_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]],
        repository_id: str,
    ):
        """
        Insert repository chunks and their embeddings into Qdrant.

        Each chunk is associated with a repository_id so that
        retrieval can be isolated to the repository being analyzed.
        """

        points = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            # Qdrant point IDs must be integers or UUIDs.
            #
            # UUID5 gives us a deterministic UUID based on:
            # repository + chunk index.
            #
            # This means indexing the same repository again produces
            # the same IDs.
            point_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"{repository_id}:{index}",
                )
            )

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "repository_id": repository_id,
                        "path": chunk["path"],
                        "content": chunk["content"],
                        "chunk_index": chunk["chunk_index"],
                    },
                )
            )

        if not points:
            return

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )

    def search(
        self,
        query_vector: list[float],
        repository_id: str,
        limit: int = 5,
    ):
        """
        Search for semantically similar chunks belonging
        only to the requested repository.
        """

        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="repository_id",
                        match=MatchValue(
                            value=repository_id,
                        ),
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
        )

        return results.points