from pydantic import BaseModel


class RepositoryDocument(BaseModel):
    path: str
    content: str
    language: str | None = None