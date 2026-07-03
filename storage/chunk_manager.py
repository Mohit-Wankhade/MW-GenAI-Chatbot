import os
import pickle

PDF_CHUNK_PATH = "storage/pdf_chunks.pkl"
GITHUB_CHUNK_PATH = "storage/github_chunks.pkl"


# ---------- PDF ----------

def save_pdf_chunks(chunks):
    with open(PDF_CHUNK_PATH, "wb") as f:
        pickle.dump(chunks, f)


def load_pdf_chunks():
    if not os.path.exists(PDF_CHUNK_PATH):
        return None

    with open(PDF_CHUNK_PATH, "rb") as f:
        return pickle.load(f)


# ---------- GitHub ----------

def save_github_chunks(chunks):
    with open(GITHUB_CHUNK_PATH, "wb") as f:
        pickle.dump(chunks, f)


def load_github_chunks():
    if not os.path.exists(GITHUB_CHUNK_PATH):
        return None

    with open(GITHUB_CHUNK_PATH, "rb") as f:
        return pickle.load(f)