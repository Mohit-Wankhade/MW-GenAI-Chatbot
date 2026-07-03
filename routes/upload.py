from fastapi import APIRouter, UploadFile, File, Depends
import shutil
import os  
from utils.chunker_metadata import chunk_pages
from rag.embed import embedding_model
from rag.index_manager import create_or_update_index
from utils.pdf_loader_metadata import extract_pages_from_pdf
from storage.vector_store_manager import set_pdf_store, set_pdf_chunks
from storage.chunk_manager import save_pdf_chunks
from utils.logger import logger
from fastapi import HTTPException
from auth.auth_dependencies import get_current_user

router = APIRouter(prefix="/upload", tags=["Upload"])
UPLOAD_FOLDER= "storage/uploads"

@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...), current_user: str =Depends(get_current_user)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    file_path= os.path.join(UPLOAD_FOLDER, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info(f"Uploaded PDF:{file.filename}")
    try:
        
        pages= extract_pages_from_pdf(file_path)
        chunks = chunk_pages(pages,file.filename)
        logger.info(f"Created {len(chunks)} chunks from {file.filename}")
        vector_store = create_or_update_index(chunks, embedding_model,"storage/pdf_index")
        logger.info(f"Indexed PDF:{file.filename}")
        set_pdf_store(vector_store)
        set_pdf_chunks(chunks)
        save_pdf_chunks(chunks)
        logger.info(f"Saved PDF chunks to storage/pdf_chunks.pkl")
    except Exception as e:
        logger.exception("PDF indexing failed.")
        raise HTTPException(status_code=500, detail= "Failed to index PDF.")
    
    return {
    "message": "PDF indexed successfully",
    "file": file.filename,
    "pages": len(pages),
    "chunks": len(chunks)
}

