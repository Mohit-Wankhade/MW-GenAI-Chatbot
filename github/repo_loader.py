import os
from git import Repo

def clone_repo(repo_url, repo_name):
    base_path="repos"
    
    os.makedirs(base_path, exist_ok=True)
    repo_path = os.path.join(base_path, repo_name)
    if os.path.exists(repo_path):
        return repo_path
    Repo.clone_from(repo_url, repo_path)
    return repo_path
