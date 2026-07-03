from langchain_text_splitters import RecursiveCharacterTextSplitter
def chunk_pages(pages, source_name):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50,)
    chunks = []
    for page in pages:
        split_chunks = splitter.split_text(page["text"])
        for chunk in split_chunks:
            chunks.append({

    "content": chunk,

    "metadata": {
        "type": "pdf",
        "source": source_name,
        "page": page["page_number"]
    }
})
    return chunks
