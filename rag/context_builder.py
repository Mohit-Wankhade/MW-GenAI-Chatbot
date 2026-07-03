def build_context(documents):
    context=""
    sources=[]
    seen=set()
    for doc in documents:
        context+=doc["content"]+"\n\n"
        metadata = doc["metadata"]
        key= tuple(sorted(metadata.items()))
        if key not in seen:
            seen.add(key)
            sources.append(metadata)
    
    return context, sources 