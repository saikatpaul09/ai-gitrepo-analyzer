import asyncio
import os

import httpx
from dotenv import load_dotenv

from app.github.document import RepositoryDocument


load_dotenv()


class GitHubFileDownloader:

    BASE_URL = "https://api.github.com"

    # Limit concurrent GitHub requests.
    MAX_CONCURRENCY = 1

    def __init__(self):

        self.token = os.getenv("GITHUB_TOKEN")

        self.headers = {
            "Accept": "application/vnd.github+json",
        }

        # GitHub token is optional.
        # Public repositories can still be accessed
        # without a token.
        if self.token:
            self.headers["Authorization"] = (
                f"Bearer {self.token}"
            )

    async def download_file(
        self,
        owner: str,
        repository: str,
        path: str,
        branch: str,
    ) -> str:

        url = (
            f"{self.BASE_URL}/repos/"
            f"{owner}/{repository}/contents/{path}"
        )

        params = {
            "ref": branch,
        }

        headers = {
            **self.headers,
            "Accept": "application/vnd.github.raw+json",
        }

        async with httpx.AsyncClient(
            headers=headers
        ) as client:

            response = await client.get(
                url,
                params=params,
            )

        response.raise_for_status()

        return response.text

    async def download_files(
        self,
        owner: str,
        repository: str,
        files: list[dict],
        branch: str,
    ) -> list[RepositoryDocument]:

        semaphore = asyncio.Semaphore(
            self.MAX_CONCURRENCY
        )

        headers = {
            **self.headers,
            "Accept": "application/vnd.github.raw+json",
        }

        async with httpx.AsyncClient(
            headers=headers
        ) as client:

            async def download(
                file: dict,
            ) -> RepositoryDocument:

                path = file["path"]

                async with semaphore:

                    url = (
                        f"{self.BASE_URL}/repos/"
                        f"{owner}/{repository}/contents/{path}"
                    )

                    response = await client.get(
                        url,
                        params={
                            "ref": branch,
                        },
                    )

                    response.raise_for_status()

                    return RepositoryDocument(
                        path=path,
                        content=response.text,
                    )

            documents = await asyncio.gather(
                *[
                    download(file)
                    for file in files
                ]
            )

        return documents