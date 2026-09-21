from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.github.document import RepositoryDocument


class RepositoryChunker:

    def __init__(
        self,
        chunk_size: int = 1500,
        chunk_overlap: int = 150,
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def chunk_document(
        self,
        document: RepositoryDocument,
    ) -> list[dict]:

        chunks = self.splitter.split_text(
            document.content
        )

        return [
            {
                "path": document.path,
                "content": chunk,
                "chunk_index": index,
            }
            for index, chunk in enumerate(chunks)
        ]