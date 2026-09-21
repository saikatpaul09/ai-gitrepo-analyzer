from pydantic import BaseModel, HttpUrl


class RepositoryInfo(BaseModel):
    owner: str
    name: str
    default_branch: str
    language: str | None
    stars: int
    forks: int


def parse_github_url(repository_url: HttpUrl) -> tuple[str, str]:
    url = str(repository_url).rstrip("/")

    parts = url.split("/")

    if len(parts) < 5 or parts[2].lower() != "github.com":
        raise ValueError("Invalid GitHub URL")

    owner = parts[3]
    repository = parts[4].removesuffix(".git")

    if not owner or not repository:
        raise ValueError("Invalid GitHub URL")

    return owner, repository