from app.github.document import RepositoryDocument
from app.rag.chunker import RepositoryChunker


document = RepositoryDocument(
    path="example.py",
    content="""
def calculate_total(items):
    total = 0

    for item in items:
        total += item.price

    return total


def calculate_average(items):
    total = calculate_total(items)

    if not items:
        return 0

    return total / len(items)
""",
)


chunker = RepositoryChunker(
    chunk_size=100,
    chunk_overlap=20,
)

chunks = chunker.chunk_document(document)

for chunk in chunks:
    print("=" * 50)
    print("PATH:", chunk["path"])
    print("CHUNK:", chunk["chunk_index"])
    print(chunk["content"])