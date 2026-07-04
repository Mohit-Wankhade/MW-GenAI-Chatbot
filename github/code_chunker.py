import hashlib
from typing import Dict, List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE


CODE_SEPARATORS = [
    "\nclass ",
    "\ndef ",
    "\nasync def ",
    "\nfunction ",
    "\nexport ",
    "\nconst ",
    "\nlet ",
    "\nvar ",
    "\npublic ",
    "\nprivate ",
    "\nprotected ",
    "\n# ",
    "\n## ",
    "\n\n",
    "\n",
    " ",
    "",
]


def _clean_content(content: str) -> str:
    return str(content or "").replace("\x00", " ").strip()


def _chunk_id(
    repo: str,
    path: str,
    chunk_index: int,
    content: str,
) -> str:
    raw = f"{repo}|{path}|{chunk_index}|{content}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def chunk_code_files(
    files: List[Dict],
    indexed_by: Optional[str] = None,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Dict]:
    """
    Splits code/documentation files into metadata-rich chunks.

    Output:
    {
        "content": "...",
        "metadata": {
            "type": "github",
            "repo": "owner/repo",
            "repo_url": "...",
            "file": "app.py",
            "path": "backend/app.py",
            "language": "python",
            "chunk_index": 0,
            "chunk_id": "...",
            "indexed_by": "username"
        }
    }
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=CODE_SEPARATORS,
    )

    chunks: List[Dict] = []
    seen = set()

    for file in files or []:
        content = _clean_content(file.get("content", ""))

        if not content:
            continue

        repo = str(file.get("repo") or "unknown-repo")
        path = str(file.get("path") or file.get("file") or "unknown-file")
        file_name = str(file.get("file") or path.split("/")[-1])
        language = str(file.get("language") or "text")

        split_chunks = splitter.split_text(content)

        for index, chunk in enumerate(split_chunks):
            clean_chunk = _clean_content(chunk)

            if not clean_chunk:
                continue

            chunk_hash = _chunk_id(
                repo=repo,
                path=path,
                chunk_index=index,
                content=clean_chunk,
            )

            if chunk_hash in seen:
                continue

            seen.add(chunk_hash)

            chunks.append(
                {
                    "content": clean_chunk,
                    "metadata": {
                        "type": "github",
                        "repo": repo,
                        "repo_url": file.get("repo_url"),
                        "file": file_name,
                        "path": path,
                        "language": language,
                        "size_bytes": file.get("size_bytes"),
                        "chunk_index": index,
                        "chunk_id": chunk_hash,
                        "indexed_by": indexed_by or file.get("indexed_by"),
                    },
                }
            )

    return chunks