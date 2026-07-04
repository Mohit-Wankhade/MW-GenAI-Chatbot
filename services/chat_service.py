from groq import Groq
from fastapi import HTTPException
from cache.redis_client import (
    get_cached_response,
    cache_response
)
from utils.logger import logger
from config import GROQ_API_KEY
from utils.guardrails import (
    validate_input,
    contains_profanity
)
import time

from utils.monitoring import (
    CHAT_REQUESTS,
    CHAT_RESPONSE_TIME
)
from storage.vector_store_manager import (
    get_pdf_store,
    get_github_store
)
from rag.retriever_manager import retrieve_all

from db.conversation_manager import (
    create_conversation,
    save_message,
    get_messages_for_llm
)

client = Groq(api_key=GROQ_API_KEY)


def normalize_query(query: str):

    return " ".join(
        query.lower().strip().split()
    )



def build_messages(query: str, conversation_id: str | None):

    # -----------------------------
    # Retrieve Documents
    # -----------------------------
    docs = retrieve_all(query)

    retrieved_context = ""

    sources = []

    for doc in docs:

        retrieved_context += doc["content"] + "\n\n"

        metadata = doc["metadata"]

        if metadata.get("type") == "pdf":

            sources.append({

                "source": metadata["source"],
                "page": metadata["page"]

            })

        elif metadata.get("type") == "github":

            sources.append({

                "source": metadata["repo"],
                "page": metadata["file"]

            })

    logger.info(f"Retrieved {len(docs)} documents")

    messages = [

        {

            "role": "system",

            "content": (
                "You're a helpful conversational RAG assistant.\n"
                "Always format your responses using Markdown.\n"
                "If you include code, ALWAYS wrap it in triple backticks with the language.\n"
                "Whenever you output source code, use fenced Markdown code blocks.\n"
                "For Python use:\n"
                "```python\n"
                "...code...\n"
                "```\n"
                "For JSON use:\n"
                "```json\n"
                "...\n"
                "```\n"
                "For Bash use:\n"
                "```bash\n"
                "...\n"
                "```\n"
                "Never output code as plain text."
                "Never output raw code without Markdown fences.\n"
                "Use bullet lists and headings where appropriate.\n"
                "Answer factual questions ONLY from retrieved context.\n"
                "If context lacks the answer, clearly say so.\n"
                "Use previous conversation only to understand references like "
                "'it', 'that', 'the previous project', etc.\n"
                "Answer factual questions ONLY using the retrieved document context.\n"
                "If the retrieved context does not contain the answer, clearly say so.\n"
                "Never hallucinate or invent information."
            )

        }

    ]

    # -----------------------------
    # Conversation History
    # -----------------------------
    if conversation_id:

        previous_messages = get_messages_for_llm(conversation_id)

        messages.extend(previous_messages)

    # -----------------------------
    # Current Question
    # -----------------------------
    messages.append(

        {

            "role": "user",

            "content": f"""
Use the previous conversation only for conversational context.

Retrieved Document Context:

{retrieved_context}

Current Question:

{query}
"""

        }

    )

    return messages, sources


def process_chat_stream(
    query: str,
    conversation_id=None,
    current_user=None
):
    start = time.time()

    CHAT_REQUESTS.inc()

    # -----------------------------
    # Guardrails
    # -----------------------------
    if not validate_input(query):
        yield "Invalid input"
        return

    if contains_profanity(query):
        yield "Inappropriate language detected"
        return

    normalized_query = normalize_query(query)

    # -----------------------------
    # Cache
    # -----------------------------
    cached = get_cached_response(normalized_query)

    if cached:
        logger.info(f"Cache HIT: {normalized_query}")
        yield cached
        return

    logger.info(f"Cache Miss: {normalized_query}")

    # -----------------------------
    # KB Check
    # -----------------------------
    pdf_store = get_pdf_store()
    github_store = get_github_store()

    if pdf_store is None and github_store is None:
        yield "No indexed PDF or GitHub repository found."
        return

    # -----------------------------
    # Conversation creation
    # -----------------------------
    if conversation_id is None:
        conversation_id = create_conversation(
            current_user,
            query[:50]
        )

    # -----------------------------
    # Build messages
    # -----------------------------
    messages, sources = build_messages(query, conversation_id)

    # -----------------------------
    # Streaming
    # -----------------------------
    full_response = ""

    try:
        logger.info("Generating streaming response...")

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            stream=True
        )

        for chunk in completion:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
                time.sleep(0.02)
                yield content

    except Exception as e:
        logger.exception("Groq Streaming API failed")
        yield "\n\nError generating response."
        return

    # -----------------------------
    # Sources formatting
    # -----------------------------
    formatted_sources = []

    for source in sources:

        src_name = source.get("source", "")
        page = source.get("page", "")

        if src_name.endswith(".pdf"):
            formatted_sources.append({
                "type": "pdf",
                "name": src_name,
                "page": page
            })
        else:
            formatted_sources.append({
                "type": "github",
                "name": f"{src_name}/{page}"
            })

    # -----------------------------
    # Append sources to response
    # -----------------------------
    #source_text = format_sources(sources)

    #if source_text:
    #    full_response += source_text
    #    yield source_text

    # -----------------------------
    # SAVE (AFTER STREAM ONLY)
    # -----------------------------
    try:
        cache_response(normalized_query, full_response)

        save_message(
            conversation_id,
            "user",
            query
        )

        save_message(
            conversation_id,
            "assistant",
            full_response,
            formatted_sources
        )
    

    except Exception:
        logger.exception("Failed to save chat after streaming")

    logger.info("Streaming completed")
    CHAT_RESPONSE_TIME.observe(
    time.time() - start
    )