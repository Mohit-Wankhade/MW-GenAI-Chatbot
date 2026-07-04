from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError

from config import REPO_FOLDER
from utils.logger import logger


def parse_github_url(repo_url: str) -> Dict[str, str]:
    """
    Validates and parses a public GitHub repository URL.

    Supported:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    """

    raw_url = str(repo_url or "").strip()

    if not raw_url:
        raise ValueError("GitHub repository URL is required.")

    parsed = urlparse(raw_url)

    if parsed.scheme != "https":
        raise ValueError("Only HTTPS GitHub repository URLs are supported.")

    if parsed.netloc.lower() != "github.com":
        raise ValueError("Only github.com repository URLs are supported.")

    parts = [part for part in parsed.path.strip("/").split("/") if part]

    if len(parts) < 2:
        raise ValueError("Invalid GitHub repository URL. Expected format: https://github.com/owner/repo")

    owner = parts[0].strip()
    repo = parts[1].strip()

    if repo.endswith(".git"):
        repo = repo[:-4]

    if not owner or not repo:
        raise ValueError("Invalid GitHub repository URL.")

    normalized_url = f"https://github.com/{owner}/{repo}.git"

    local_dir_name = f"{owner}__{repo}"

    return {
        "owner": owner,
        "repo": repo,
        "repo_label": f"{owner}/{repo}",
        "local_dir_name": local_dir_name,
        "normalized_url": normalized_url,
    }


def clone_repo(
    repo_url: str,
    repo_name: str | None = None,
    refresh_existing: bool = True,
) -> str:
    """
    Clones a GitHub repository into repos/{owner}__{repo}.

    If the repo already exists:
    - validates that it is a Git repo
    - optionally pulls latest changes

    Kept compatible with old call style:
    clone_repo(repo_url, repo_name)
    """

    repo_info = parse_github_url(repo_url)

    base_path = Path(REPO_FOLDER)
    base_path.mkdir(parents=True, exist_ok=True)

    safe_repo_dir = repo_info["local_dir_name"]

    if repo_name:
        # Backward compatibility, but avoid unsafe folder names.
        safe_repo_dir = "".join(
            char if char.isalnum() or char in {"_", "-", "."} else "_"
            for char in repo_name
        ).strip("._") or repo_info["local_dir_name"]

    repo_path = base_path / safe_repo_dir

    if repo_path.exists():
        try:
            repo = Repo(str(repo_path))

            if refresh_existing:
                logger.info("Repository already exists. Pulling latest changes: %s", repo_path)

                try:
                    repo.remotes.origin.pull()

                except Exception:
                    logger.warning(
                        "Could not pull latest changes for %s. Using existing local copy.",
                        repo_info["repo_label"],
                    )

            return str(repo_path)

        except (InvalidGitRepositoryError, NoSuchPathError):
            raise ValueError(
                f"Path already exists but is not a valid Git repository: {repo_path}"
            )

    logger.info(
        "Cloning repository. repo=%s target=%s",
        repo_info["repo_label"],
        repo_path,
    )

    Repo.clone_from(
        repo_info["normalized_url"],
        str(repo_path),
        multi_options=["--depth=1"],
    )

    return str(repo_path)