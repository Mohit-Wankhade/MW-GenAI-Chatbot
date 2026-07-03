from rag.index_manager import load_vector_store

from rag.embed import embedding_model

from storage.chunk_manager import (
    load_pdf_chunks,
    load_github_chunks
)

PDF_INDEX_PATH = "storage/pdf_index"
GITHUB_INDEX_PATH = "storage/github_index"

pdf_store = None
github_store = None

pdf_chunks = None
github_chunks = None


# ---------------- PDF ----------------

def set_pdf_store(store):
    global pdf_store
    pdf_store = store


def get_pdf_store():
    global pdf_store

    if pdf_store is None:
        pdf_store = load_vector_store(
            embedding_model,
            PDF_INDEX_PATH
        )

    return pdf_store


# ---------------- GitHub ----------------

def set_github_store(store):
    global github_store
    github_store = store


def get_github_store():
    global github_store

    if github_store is None:
        github_store = load_vector_store(
            embedding_model,
            GITHUB_INDEX_PATH
        )

    return github_store


# ---------------- PDF Chunks ----------------

def set_pdf_chunks(chunks):
    global pdf_chunks
    pdf_chunks = chunks


def get_pdf_chunks():
    global pdf_chunks

    if pdf_chunks is None:
        pdf_chunks = load_pdf_chunks()

    return pdf_chunks


# ---------------- GitHub Chunks ----------------

def set_github_chunks(chunks):
    global github_chunks
    github_chunks = chunks


def get_github_chunks():
    global github_chunks

    if github_chunks is None:
        github_chunks = load_github_chunks()

    return github_chunks