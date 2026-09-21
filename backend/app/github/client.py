import os

import httpx
from dotenv import load_dotenv

from app.github.repository import RepositoryInfo


load_dotenv()


class GitHubClient:

    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")

        self.headers = {
            "Accept": "application/vnd.github+json",
        }

        # GitHub token is optional.
        # If configured, use authenticated requests.
        if self.token:
            self.headers["Authorization"] = (
                f"Bearer {self.token}"
            )

    async def get_repository(
        self,
        owner: str,
        repository: str,
    ) -> RepositoryInfo:

        url = (
            f"{self.BASE_URL}/repos/"
            f"{owner}/{repository}"
        )

        async with httpx.AsyncClient(
            headers=self.headers
        ) as client:

            response = await client.get(url)

        response.raise_for_status()

        data = response.json()

        return RepositoryInfo(
            owner=data["owner"]["login"],
            name=data["name"],
            default_branch=data["default_branch"],
            language=data["language"],
            stars=data["stargazers_count"],
            forks=data["forks_count"],
        )

    async def get_repository_tree(
        self,
        owner: str,
        repository: str,
        branch: str,
    ) -> list[dict]:

        url = (
            f"{self.BASE_URL}/repos/"
            f"{owner}/{repository}/git/trees/{branch}"
        )

        params = {
            "recursive": "1",
        }

        async with httpx.AsyncClient(
            headers=self.headers
        ) as client:

            response = await client.get(
                url,
                params=params,
            )

        response.raise_for_status()

        data = response.json()

        return data.get("tree", [])