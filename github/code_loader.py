from pathlib import Path
from typing import Dict, List, Optional

from config import (
    GITHUB_ALLOWED_EXTENSIONS,
    GITHUB_MAX_FILE_SIZE_KB,
    GITHUB_MAX_FILES,
)
from utils.logger import logger


SUPPORTED_EXTENSIONS = set(GITHUB_ALLOWED_EXTENSIONS)

IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
    ".vite",
    ".cache",
    "target",
    "out",
}

BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".rar",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".class",
    ".jar",
    ".pyc",
    ".pkl",
    ".faiss",
    ".sqlite",
    ".db",
}


def _is_supported_file(path: Path) -> bool:
    suffix = path.suffix.lower()

    if suffix in BINARY_EXTENSIONS:
        return False

    return suffix in SUPPORTED_EXTENSIONS


def _read_text_file(path: Path) -> Optional[str]:
    try:
        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    except Exception:
        logger.warning("Could not read file: %s", path)
        return None


def _language_from_extension(path: Path) -> str:
    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".md": "markdown",
        ".txt": "text",
        ".json": "json",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".toml": "toml",
        ".ini": "ini",
    }

    return mapping.get(path.suffix.lower(), path.suffix.lower().replace(".", "") or "text")


def load_code_files(
    repo_path: str,
    repo_name: str,
    repo_url: Optional[str] = None,
    indexed_by: Optional[str] = None,
) -> List[Dict]:
    """
    Loads supported code/documentation files from a cloned repository.

    Output:
    [
        {
            "repo": "owner/repo",
            "repo_url": "...",
            "file": "app.py",
            "path": "backend/app.py",
            "absolute_path": "...",
            "language": "python",
            "size_bytes": 1234,
            "content": "..."
        }
    ]
    """

    root_path = Path(repo_path).resolve()

    if not root_path.exists():
        raise FileNotFoundError(f"Repository path not found: {repo_path}")

    files: List[Dict] = []
    max_file_size_bytes = GITHUB_MAX_FILE_SIZE_KB * 1024

    for path in root_path.rglob("*"):
        if len(files) >= GITHUB_MAX_FILES:
            logger.info(
                "GitHub file load limit reached. repo=%s max_files=%s",
                repo_name,
                GITHUB_MAX_FILES,
            )
            break

        if not path.is_file():
            continue

        relative_parts = path.relative_to(root_path).parts

        if any(part in IGNORED_DIRECTORIES for part in relative_parts):
            continue

        if not _is_supported_file(path):
            continue

        try:
            size_bytes = path.stat().st_size

        except OSError:
            continue

        if size_bytes <= 0:
            continue

        if size_bytes > max_file_size_bytes:
            logger.info(
                "Skipping large file. repo=%s file=%s size_kb=%.2f",
                repo_name,
                path,
                size_bytes / 1024,
            )
            continue

        content = _read_text_file(path)

        if not content or not content.strip():
            continue

        relative_path = path.relative_to(root_path).as_posix()

        files.append(
            {
                "repo": repo_name,
                "repo_url": repo_url,
                "file": path.name,
                "path": relative_path,
                "absolute_path": str(path),
                "language": _language_from_extension(path),
                "size_bytes": size_bytes,
                "content": content,
                "indexed_by": indexed_by,
            }
        )

    logger.info(
        "Loaded code files. repo=%s count=%s",
        repo_name,
        len(files),
    )

    return files