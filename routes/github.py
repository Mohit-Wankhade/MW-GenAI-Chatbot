from fastapi import APIRouter

from utils.monitoring import GITHUB_REPOS
router = APIRouter(
    prefix="/github",
    tags=["GitHub"]
)
from pydantic import BaseModel
class GitHubRequest(BaseModel):
    repo_url: str

from github.repo_loader import clone_repo
from github.code_loader import load_code_files
from github.code_chunker import chunk_code_files
from rag.index_manager import create_or_update_index
from rag.embed import embedding_model
from storage.vector_store_manager import set_github_chunks, set_github_store
from storage.chunk_manager import save_github_chunks
from utils.logger import logger
from fastapi import HTTPException, Depends
from git.exc import GitCommandError
from auth.auth_dependencies import get_current_user

@router.post("/index")
def index_github(request: GitHubRequest, current_user:str= Depends(get_current_user)):
    repo_name = request.repo_url.rstrip("/").split("/")[-1]
    try:
        repo_path = clone_repo(request.repo_url, repo_name)
        logger.info(f"Repository Cloned:{repo_name}")
    except GitCommandError:
        logger.exception("Git Clone failed.")
        raise HTTPException(status_code=400, detail="Unable to clone repository.")
    try:
        files= load_code_files(repo_path,repo_name)
        logger.info(f"Loaded:{len(files)} source files.")
        chunks= chunk_code_files(files)
        logger.info(f"Created:{len(chunks)} code chunks")
        vector_store = create_or_update_index(chunks,embedding_model,"storage/github_index")
        set_github_store(vector_store)
        set_github_chunks(chunks)
        save_github_chunks(chunks)
        GITHUB_REPOS.inc()
    except Exception:
        logger.exception("GitHub indexing failed.")
        raise HTTPException(status_code=500, detail="Failed to index repository.")

    
    return {"message": "Repository indexed successfully",
            "repo": repo_name,
            "files": len(files),
            "chunks":len(chunks)}