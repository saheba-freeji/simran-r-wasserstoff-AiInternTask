from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime
from typing import List
import json

from app.services.document_parser import DocumentParser
from app.services.vector_store import VectorStore
from app.services.theme_identifier import ThemeIdentifier
from app.models.document import Document, DocumentResponse, ChatResponse
from app.models.api import ChatRequest
from app.config import get_settings

app = FastAPI(title="Document Theme Identifier")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_parser = DocumentParser()
vector_store = VectorStore()

def get_theme_identifier():
    """Get ThemeIdentifier instance with API key validation"""
    settings = get_settings()
    api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not set. Please provide your API key in the settings."
        )
    
    return ThemeIdentifier(api_key)

# Store uploaded documents in memory (replace with proper database in production)
documents = {}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Save file temporarily
        temp_path = f"files/{file.filename}"
        with open(temp_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        # Parse document
        parsed_doc = document_parser.parse_file(temp_path)
        
        # Generate document ID
        doc_id = f"DOC{len(documents)+1:03d}"
        
        # Create document record
        doc = Document(
            id=doc_id,
            filename=file.filename,
            content=parsed_doc["text"],
            doc_type=parsed_doc["type"],
            upload_date=datetime.now(),
            metadata={"source": parsed_doc["source"]}
        )
        
        # Store document
        documents[doc_id] = doc
        
        # Add to vector store
        vector_store.add_document(
            doc_id=doc_id,
            content=doc.content,
            metadata={"filename": doc.filename, "type": doc.doc_type}
        )
        
        # Clean up temp file
        os.remove(temp_path)
        
        return {"document_id": doc_id, "message": "Document uploaded successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(
    request: ChatRequest,
    theme_identifier: ThemeIdentifier = Depends(get_theme_identifier)
):
    """Process a chat query and identify themes"""
    try:
        if len(documents) == 0:
            raise HTTPException(status_code=400, detail="No documents uploaded yet")
            
        # Search relevant documents
        search_results = vector_store.search(request.query)
        
        # Prepare document responses
        responses = []
        for result in search_results:
            doc_id = result["id"]
            doc = documents[doc_id]
            
            # Split content into paragraphs and find relevant one
            paragraphs = doc.content.split('\n\n')
            best_para_idx = next((i for i, p in enumerate(paragraphs) 
                                if request.query.lower() in p.lower()), 0)
            
            # Get page and paragraph numbers
            page_num = doc.metadata.get("pages", [])[best_para_idx]["page"] if doc.metadata.get("pages") else 1
            para_num = doc.metadata.get("pages", [])[best_para_idx]["paragraph"] if doc.metadata.get("pages") else 1
            
            responses.append(DocumentResponse(
                document_id=doc_id,
                answer=paragraphs[best_para_idx],
                citation=f"Page {page_num}, Para {para_num}"
            ))
        
        # Identify themes
        themes = theme_identifier.identify_themes(responses)
        
        return ChatResponse(
            themes=themes,
            raw_responses=responses
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "type": doc.doc_type,
            "upload_date": doc.upload_date
        }
        for doc in documents.values()
    ]