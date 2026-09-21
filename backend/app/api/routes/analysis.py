import asyncio
import time
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl

from app.agents.orchestrator import AnalysisOrchestrator
from app.github.client import GitHubClient
from app.github.downloader import GitHubFileDownloader
from app.github.repository import parse_github_url
from app.github.scanner import RepositoryScanner
from app.llm.client import OpenAIClient
from app.rag.chunker import RepositoryChunker
from app.rag.embeddings import EmbeddingService
from app.rag.qdrant import QdrantService
from app.rag.retriever import RepositoryRetriever


router = APIRouter(
    prefix="/api/v1/analyses",
    tags=["Analysis"],
)


class AnalysisRequest(BaseModel):
    repository_url: HttpUrl


# ---------------------------------------------------------
# Shared services
# ---------------------------------------------------------

github_client = GitHubClient()

repository_scanner = RepositoryScanner(
    github_client=github_client,
)

file_downloader = GitHubFileDownloader()

repository_chunker = RepositoryChunker()

embedding_service = EmbeddingService()

qdrant_service = QdrantService()

retriever = RepositoryRetriever(
    embedding_service=embedding_service,
    qdrant_service=qdrant_service,
)

llm_client = OpenAIClient()

analysis_orchestrator = AnalysisOrchestrator(
    retriever=retriever,
    llm_client=llm_client,
)


# ---------------------------------------------------------
# In-memory analysis jobs
# ---------------------------------------------------------

analysis_jobs: dict[str, dict] = {}


def create_job() -> str:
    analysis_id = str(uuid.uuid4())

    analysis_jobs[analysis_id] = {
        "analysis_id": analysis_id,
        "status": "queued",
        "stage": "queued",
        "progress": 0,
        "message": "Analysis queued",
        "result": None,
        "error": None,
    }

    return analysis_id


def update_job(
    analysis_id: str,
    *,
    status: str | None = None,
    stage: str | None = None,
    progress: int | None = None,
    message: str | None = None,
    result: dict | None = None,
    error: str | None = None,
):
    job = analysis_jobs.get(analysis_id)

    if not job:
        return

    if status is not None:
        job["status"] = status

    if stage is not None:
        job["stage"] = stage

    if progress is not None:
        job["progress"] = progress

    if message is not None:
        job["message"] = message

    if result is not None:
        job["result"] = result

    if error is not None:
        job["error"] = error


# ---------------------------------------------------------
# Background analysis
# ---------------------------------------------------------

async def run_analysis(
    analysis_id: str,
    repository_url: str,
):
    request_start = time.perf_counter()

    try:

        # -------------------------------------------------
        # 1. Parse repository
        # -------------------------------------------------

        update_job(
            analysis_id,
            status="running",
            stage="scanning",
            progress=5,
            message="Reading repository information...",
        )

        owner, repository = parse_github_url(repository_url)

        print(
            f"\nAnalyzing repository: "
            f"{owner}/{repository}"
        )

        # -------------------------------------------------
        # 2. Repository metadata
        # -------------------------------------------------

        stage_start = time.perf_counter()

        repository_info = await github_client.get_repository(
            owner=owner,
            repository=repository,
        )

        print(
            f"[timing] Repository metadata: "
            f"{time.perf_counter() - stage_start:.2f}s"
        )

        update_job(
            analysis_id,
            stage="scanning",
            progress=10,
            message="Scanning repository files...",
        )

        # -------------------------------------------------
        # 3. Repository tree
        # -------------------------------------------------

        stage_start = time.perf_counter()

        tree = await github_client.get_repository_tree(
            owner=owner,
            repository=repository,
            branch=repository_info.default_branch,
        )

        print(
            f"[timing] Repository tree: "
            f"{time.perf_counter() - stage_start:.2f}s"
        )

        # -------------------------------------------------
        # 4. Filter files
        # -------------------------------------------------

        stage_start = time.perf_counter()

        files = repository_scanner.filter_tree(tree)

        print(
            f"[timing] File filtering: "
            f"{time.perf_counter() - stage_start:.2f}s"
        )

        print(
            f"Supported files: {len(files)}"
        )

        if not files:
            raise ValueError(
                "No supported source files found "
                "in repository."
            )

        repository_id = (
            f"{owner}_{repository}"
        )

        update_job(
            analysis_id,
            stage="downloading",
            progress=20,
            message=f"Downloading {len(files)} repository files...",
        )

        # -------------------------------------------------
        # 5. Download files
        # -------------------------------------------------

        stage_start = time.perf_counter()

        documents = await file_downloader.download_files(
            owner=owner,
            repository=repository,
            files=files,
            branch=repository_info.default_branch,
        )

        print(
            f"[timing] File downloads: "
            f"{time.perf_counter() - stage_start:.2f}s"
        )

        update_job(
            analysis_id,
            stage="chunking",
            progress=30,
            message="Preparing repository content...",
        )

        # -------------------------------------------------
        # 6. Chunk documents
        # -------------------------------------------------

        stage_start = time.perf_counter()

        chunks = []

        for document in documents:
            chunks.extend(
                repository_chunker.chunk_document(
                    document
                )
            )

        print(
            f"[timing] Chunking: "
            f"{time.perf_counter() - stage_start:.2f}s"
        )

        if not chunks:
            raise ValueError(
                "No content could be chunked "
                "from repository."
            )

        print(
            f"Generated {len(chunks)} chunks"
        )

        update_job(
            analysis_id,
            stage="embedding",
            progress=40,
            message=f"Generating embeddings for {len(chunks)} chunks...",
        )

        # -------------------------------------------------
        # 7. Generate embeddings
        # -------------------------------------------------

        stage_start = time.perf_counter()

        texts = [
            chunk["content"]
            for chunk in chunks
        ]

        embeddings = await asyncio.to_thread(
            embedding_service.embed,
            texts,
        )

        print(
            f"[timing] Embeddings: "
            f"{time.perf_counter() - stage_start:.2f}s"
        )

        update_job(
            analysis_id,
            stage="indexing",
            progress=65,
            message="Indexing repository in Qdrant...",
        )

        # -------------------------------------------------
        # 8. Qdrant indexing
        # -------------------------------------------------

        qdrant_service.create_collection()

        stage_start = time.perf_counter()

        qdrant_service.insert_chunks(
            chunks=chunks,
            embeddings=embeddings,
            repository_id=repository_id,
        )

        print(
            f"[timing] Qdrant indexing: "
            f"{time.perf_counter() - stage_start:.2f}s"
        )

        update_job(
            analysis_id,
            stage="ai_analysis",
            progress=70,
            message="Running engineering analysis...",
        )

        # -------------------------------------------------
        # 9. AI analysis
        # -------------------------------------------------

        print(
            f"\nStarting analysis for: "
            f"{repository_id}"
        )

        stage_start = time.perf_counter()

        report = await analysis_orchestrator.analyze(
            repository_id=repository_id,
        )

        ai_analysis_time = (
            time.perf_counter() - stage_start
        )

        print(
            f"[timing] AI analysis: "
            f"{ai_analysis_time:.2f}s"
        )

        # -------------------------------------------------
        # 10. Complete
        # -------------------------------------------------

        total_time = (
            time.perf_counter() - request_start
        )

        result = {
            "repository": repository_info.model_dump(),
            "repository_id": repository_id,
            "file_count": len(files),
            "document_count": len(documents),
            "chunk_count": len(chunks),
            "embedding_count": len(embeddings),
            "analysis_time_seconds": round(
                total_time,
                2,
            ),
            "report": report.model_dump(),
        }

        print(
            f"\n[timing] TOTAL: "
            f"{total_time:.2f}s\n"
        )

        update_job(
            analysis_id,
            status="completed",
            stage="completed",
            progress=100,
            message="Engineering analysis completed.",
            result=result,
        )

    except Exception as exc:

        print(
            f"\nAnalysis failed: "
            f"{analysis_id}"
        )

        print(exc)

        update_job(
            analysis_id,
            status="failed",
            stage="failed",
            message="Analysis failed.",
            error=str(exc),
        )


# ---------------------------------------------------------
# Create analysis
# ---------------------------------------------------------

@router.post(
    "",
    status_code=202,
)
async def create_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
):
    analysis_id = create_job()

    background_tasks.add_task(
        run_analysis,
        analysis_id,
        str(request.repository_url),
    )

    return {
        "analysis_id": analysis_id,
        "status": "queued",
        "message": "Analysis started.",
    }


# ---------------------------------------------------------
# Get analysis status
# ---------------------------------------------------------

@router.get(
    "/{analysis_id}",
)
async def get_analysis(
    analysis_id: str,
):
    job = analysis_jobs.get(analysis_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    return job