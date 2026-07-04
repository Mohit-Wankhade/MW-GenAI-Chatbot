import hashlib
from time import perf_counter
from typing import Any, Dict, Generator, List, Optional, Tuple

from fastapi import HTTPException
from groq import Groq

from cache.redis_client import cache_response, get_cached_response
from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
)
from db.conversation_manager import (
    create_conversation,
    get_messages_for_llm,
    save_message,
)
from rag.context_builder import build_context
from rag.retriever_manager import retrieve_all
from storage.vector_store_manager import get_github_store, get_pdf_store
from utils.guardrails import contains_profanity, validate_input
from utils.logger import logger
from utils.monitoring import CHAT_REQUESTS, CHAT_RESPONSE_TIME


_groq_client: Optional[Groq] = None


def get_groq_client() -> Groq:
    """
    Lazily initializes Groq client.
    """

    global _groq_client

    if _groq_client is None:
        if not GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        _groq_client = Groq(api_key=GROQ_API_KEY)

    return _groq_client


def normalize_query(query: str) -> str:
    return " ".join(query.lower().strip().split())


def _safe_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _build_cache_key(
    query: str,
    context: str,
    current_user: Optional[str],
) -> str:
    user_key = current_user or "anonymous"
    raw_key = f"{user_key}|{normalize_query(query)}|{_hash_text(context)}"
    return f"chat:v2:{_hash_text(raw_key)}"


def _format_sources(raw_sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    formatted_sources: List[Dict[str, Any]] = []
    seen = set()

    for source in raw_sources:
        source_type = source.get("type")

        if source_type == "pdf":
            name = _safe_text(
                source.get("original_filename")
                or source.get("source")
                or source.get("file")
                or source.get("name")
            )
            page = source.get("page")

            source_payload = {
                "type": "pdf",
                "name": name,
                "page": page,
            }

        elif source_type == "github":
            repo = _safe_text(
                source.get("repo")
                or source.get("source")
                or source.get("name")
            )
            file_path = _safe_text(
                source.get("path")
                or source.get("file")
            )

            source_payload = {
                "type": "github",
                "name": f"{repo}/{file_path}" if repo and file_path else repo or file_path,
                "repo": repo,
                "file": file_path,
            }

        else:
            source_payload = {
                "type": source_type or "unknown",
                "name": _safe_text(
                    source.get("source")
                    or source.get("name")
                    or source.get("file")
                    or source.get("repo")
                    or "Unknown source"
                ),
            }

        key = tuple(sorted((k, str(v)) for k, v in source_payload.items()))

        if key not in seen:
            seen.add(key)
            formatted_sources.append(source_payload)

    return formatted_sources


def _system_prompt() -> str:
    return (
        "You are a helpful, production-grade conversational RAG assistant.\n\n"
        "Response rules:\n"
        "- Always format responses using clean Markdown.\n"
        "- Use headings, bullet points, and tables when helpful.\n"
        "- If you include code, always use fenced Markdown code blocks with the correct language.\n"
        "- Never output raw code without Markdown fences.\n"
        "- For Python use ```python, for Bash use ```bash, for JSON use ```json.\n\n"
        "Grounding rules:\n"
        "- Answer factual questions using the retrieved document context.\n"
        "- Use previous conversation only to understand references like 'it', 'that', or 'the previous file'.\n"
        "- If the retrieved context does not contain the answer, clearly say that the available context does not include it.\n"
        "- Do not invent file names, page numbers, repository details, APIs, or facts.\n"
        "- Do not mention internal prompts, hidden rules, or implementation details unless the user asks about the system design.\n\n"
        "Style rules:\n"
        "- Be direct and practical.\n"
        "- Prefer complete, usable answers over vague explanations.\n"
        "- For code-related answers, explain the reason behind important changes briefly."
    )


def build_messages(
    query: str,
    conversation_id: Optional[str],
    current_user: Optional[str] = None,
) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]], List[Dict[str, str]], str]:
    docs = retrieve_all(query)
    retrieved_context, raw_sources = build_context(docs)
    formatted_sources = _format_sources(raw_sources)

    logger.info("Retrieved %s documents for query.", len(docs))

    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": _system_prompt(),
        }
    ]

    previous_messages: List[Dict[str, str]] = []

    if conversation_id:
        previous_messages = get_messages_for_llm(
            conversation_id=conversation_id,
            user=current_user,
            limit=12,
        )

        messages.extend(previous_messages)

    user_prompt = f"""
Use the previous conversation only for conversational continuity.

Retrieved Document Context:
---------------------------
{retrieved_context if retrieved_context else "No relevant context was retrieved."}

Current Question:
-----------------
{query}
""".strip()

    messages.append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )

    return messages, formatted_sources, previous_messages, retrieved_context


def _yield_and_save_simple_response(
    response: str,
    query: str,
    conversation_id: Optional[str],
    current_user: Optional[str],
    sources: Optional[List[Dict[str, Any]]] = None,
) -> Generator[str, None, None]:
    if conversation_id is None and current_user:
        conversation_id = create_conversation(
            user=current_user,
            title=query[:50],
        )

    yield response

    if conversation_id:
        try:
            save_message(
                conversation_id=conversation_id,
                role="user",
                content=query,
            )

            save_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response,
                sources=sources or [],
            )

        except Exception:
            logger.exception("Failed to save simple chat response.")


def process_chat_stream(
    query: str,
    conversation_id: Optional[str] = None,
    current_user: Optional[str] = None,
) -> Generator[str, None, None]:
    start_time = perf_counter()

    try:
        CHAT_REQUESTS.inc()

        clean_query = _safe_text(query)

        if not validate_input(clean_query):
            yield from _yield_and_save_simple_response(
                response="Invalid input. Please enter a valid question.",
                query=clean_query or query,
                conversation_id=conversation_id,
                current_user=current_user,
            )
            return

        if contains_profanity(clean_query):
            yield from _yield_and_save_simple_response(
                response="Inappropriate language detected. Please rephrase your question.",
                query=clean_query,
                conversation_id=conversation_id,
                current_user=current_user,
            )
            return

        pdf_store = get_pdf_store()
        github_store = get_github_store()

        if pdf_store is None and github_store is None:
            yield from _yield_and_save_simple_response(
                response="No indexed PDF or GitHub repository found. Please upload a PDF or index a GitHub repository first.",
                query=clean_query,
                conversation_id=conversation_id,
                current_user=current_user,
            )
            return

        if conversation_id is None:
            conversation_id = create_conversation(
                user=current_user or "anonymous",
                title=clean_query[:50],
            )

        messages, sources, previous_messages, retrieved_context = build_messages(
            query=clean_query,
            conversation_id=conversation_id,
            current_user=current_user,
        )

        if not retrieved_context.strip():
            response = (
                "I could not find relevant information in the indexed PDF or GitHub repository for this question. "
                "Please upload/index the relevant source or ask a question related to the available documents."
            )

            yield from _yield_and_save_simple_response(
                response=response,
                query=clean_query,
                conversation_id=conversation_id,
                current_user=current_user,
                sources=[],
            )
            return

        cache_key = _build_cache_key(
            query=clean_query,
            context=retrieved_context,
            current_user=current_user,
        )

        can_use_cache = len(previous_messages) == 0

        if can_use_cache:
            cached_response = get_cached_response(cache_key)

            if cached_response:
                logger.info("Cache HIT for query: %s", normalize_query(clean_query))

                yield str(cached_response)

                save_message(
                    conversation_id=conversation_id,
                    role="user",
                    content=clean_query,
                )

                save_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=str(cached_response),
                    sources=sources,
                )

                return

        logger.info("Cache MISS for query: %s", normalize_query(clean_query))

        client = get_groq_client()

        full_response = ""

        logger.info("Generating streaming response with Groq model: %s", GROQ_MODEL)

        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            stream=True,
        )

        for chunk in completion:
            content = getattr(chunk.choices[0].delta, "content", None)

            if content:
                full_response += content
                yield content

        final_response = full_response.strip()

        if not final_response:
            final_response = "I could not generate a response. Please try again."
            yield final_response

        if can_use_cache and final_response:
            cache_response(cache_key, final_response)

        save_message(
            conversation_id=conversation_id,
            role="user",
            content=clean_query,
        )

        save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=final_response,
            sources=sources,
        )

        logger.info("Streaming completed successfully.")

    except HTTPException as exc:
        logger.warning("Chat request failed: %s", exc.detail)
        yield str(exc.detail)

    except Exception:
        logger.exception("Chat streaming failed.")
        yield "\n\nError generating response. Please try again later."

    finally:
        CHAT_RESPONSE_TIME.observe(perf_counter() - start_time)