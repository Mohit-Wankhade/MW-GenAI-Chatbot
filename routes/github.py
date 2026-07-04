from fastapi import APIRouter, Depends, HTTPException, status
from git.exc import GitCommandError
from pydantic import BaseModel, ConfigDict, Field, field_validator

from auth.auth_dependencies import get_current_user
from config import GITHUB_INDEX_PATH
from github.code_chunker import chunk_code_files
from github.code_loader import load_code_files
from github.repo_loader import clone_repo, parse_github_url
from rag.embed import embedding_model
from rag.index_manager import create_or_update_index
from storage.chunk_manager import append_github_chunks
from storage.vector_store_manager import set_github_chunks, set_github_store
from utils.logger import logger
from utils.monitoring import GITHUB_REPOS


router = APIRouter(
    prefix="/github",
    tags=["GitHub"],
)


class GitHubRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    repo_url: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="Public GitHub repository URL, e.g. https://github.com/owner/repo",
    )

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, value: str) -> str:
        parse_github_url(value)
        return value.strip()


@router.post("/index")
def index_github(
    request: GitHubRequest,
    current_user: str = Depends(get_current_user),
):
    repo_info = parse_github_url(request.repo_url)
    repo_label = f"{repo_info['owner']}/{repo_info['repo']}"

    try:
        repo_path = clone_repo(request.repo_url)

        logger.info(
            "Repository cloned or updated. user=%s repo=%s path=%s",
            current_user,
            repo_label,
            repo_path,
        )

    except GitCommandError:
        logger.exception("Git clone/pull failed. repo=%s", repo_label)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to clone repository. Please check that the GitHub repository is public and the URL is correct.",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    try:
        files = load_code_files(
            repo_path=repo_path,
            repo_name=repo_label,
            repo_url=repo_info["normalized_url"],
            indexed_by=current_user,
        )

        if not files:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No supported source/code files found in this repository.",
            )

        logger.info(
            "Loaded source files. repo=%s files=%s",
            repo_label,
            len(files),
        )

        chunks = chunk_code_files(
            files=files,
            indexed_by=current_user,
        )

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No searchable chunks could be created from this repository.",
            )

        logger.info(
            "Created code chunks. repo=%s chunks=%s",
            repo_label,
            len(chunks),
        )

        vector_store = create_or_update_index(
            chunks=chunks,
            embedding_model=embedding_model,
            index_path=GITHUB_INDEX_PATH,
        )

        all_github_chunks = append_github_chunks(chunks)

        set_github_store(vector_store)
        set_github_chunks(all_github_chunks)

        GITHUB_REPOS.inc()

        logger.info(
            "GitHub repository indexed successfully. repo=%s total_github_chunks=%s",
            repo_label,
            len(all_github_chunks),
        )

        return {
            "message": "Repository indexed successfully.",
            "repo": repo_label,
            "repo_url": repo_info["normalized_url"],
            "files": len(files),
            "chunks": len(chunks),
            "total_github_chunks": len(all_github_chunks),
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("GitHub indexing failed. repo=%s", repo_label)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to index repository.",
        )