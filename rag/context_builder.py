import json
from typing import Any, Dict, Iterable, List, Tuple

from config import MAX_CONTEXT_CHARS


def _get_content(document: Any) -> str:
    if isinstance(document, dict):
        return str(document.get("content", "")).strip()

    return str(getattr(document, "page_content", "")).strip()


def _get_metadata(document: Any) -> Dict[str, Any]:
    if isinstance(document, dict):
        metadata = document.get("metadata", {})
    else:
        metadata = getattr(document, "metadata", {})

    return metadata if isinstance(metadata, dict) else {}


def _metadata_key(metadata: Dict[str, Any]) -> str:
    return json.dumps(
        metadata,
        sort_keys=True,
        default=str,
    )


def _content_key(content: str) -> str:
    return " ".join(content.lower().split())


def _format_context_block(index: int, content: str, metadata: Dict[str, Any]) -> str:
    source_type = metadata.get("type", "unknown")

    if source_type == "pdf":
        source = metadata.get("source") or metadata.get("file") or "PDF"
        page = metadata.get("page", "unknown")

        header = f"[Source {index} | PDF: {source} | Page: {page}]"

    elif source_type == "github":
        repo = metadata.get("repo") or metadata.get("source") or "GitHub Repository"
        file_path = metadata.get("file") or metadata.get("path") or "unknown file"

        header = f"[Source {index} | GitHub: {repo} | File: {file_path}]"

    else:
        source = (
            metadata.get("source")
            or metadata.get("name")
            or metadata.get("file")
            or metadata.get("repo")
            or "Unknown Source"
        )

        header = f"[Source {index} | {source}]"

    return f"{header}\n{content.strip()}"


def build_context(
    documents: Iterable[Any],
    max_chars: int = MAX_CONTEXT_CHARS,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Builds clean RAG context and source metadata.

    Accepts both:
    - dict format: {"content": "...", "metadata": {...}}
    - LangChain Document format: Document(page_content="...", metadata={...})

    Returns:
    - context string for LLM prompt
    - deduplicated source metadata list
    """

    context_blocks: List[str] = []
    sources: List[Dict[str, Any]] = []

    seen_content = set()
    seen_sources = set()

    total_chars = 0
    source_index = 1

    for document in documents or []:
        content = _get_content(document)

        if not content:
            continue

        normalized_content_key = _content_key(content)

        if normalized_content_key in seen_content:
            continue

        seen_content.add(normalized_content_key)

        metadata = _get_metadata(document)
        metadata_key = _metadata_key(metadata)

        if metadata_key not in seen_sources:
            seen_sources.add(metadata_key)
            sources.append(metadata)

        context_block = _format_context_block(
            index=source_index,
            content=content,
            metadata=metadata,
        )

        remaining_chars = max_chars - total_chars

        if remaining_chars <= 0:
            break

        if len(context_block) > remaining_chars:
            context_block = context_block[:remaining_chars].rstrip() + "\n[Content truncated]"

        context_blocks.append(context_block)
        total_chars += len(context_block)
        source_index += 1

    return "\n\n---\n\n".join(context_blocks).strip(), sources