from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_code_files(files):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = []
    for file in files:
        split_chunks = splitter.split_text(file["content"])
        for chunk in split_chunks:
            chunks.append({"content": chunk, "metadata": {"type": "github","repo": file["repo"],"file": file["file"],"path": file["path"] }})
    return chunks