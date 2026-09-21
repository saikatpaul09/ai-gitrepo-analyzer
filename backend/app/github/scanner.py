from app.github.client import GitHubClient


IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    "node_modules",
    "dist",
    "build",
    ".next",
    "coverage",
    "__pycache__",
    ".venv",
    "venv",
}


ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rs",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".cs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".kts",
    ".sql",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".xml",
    ".md",
    ".dockerfile",
}


class RepositoryScanner:

    def __init__(self, github_client: GitHubClient):
        self.github_client = github_client

    def filter_tree(
        self,
        tree: list[dict],
    ) -> list[dict]:

        filtered_files = []

        for item in tree:
            if item.get("type") != "blob":
                continue

            path = item.get("path", "")

            path_parts = path.split("/")

            if any(
                directory in IGNORED_DIRECTORIES
                for directory in path_parts
            ):
                continue

            filename = path_parts[-1]

            if "." in filename:
                extension = "." + filename.split(".")[-1].lower()

                if extension not in ALLOWED_EXTENSIONS:
                    continue

            filtered_files.append(item)

        return filtered_files