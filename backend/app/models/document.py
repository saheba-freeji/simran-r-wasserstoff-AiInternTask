from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class Document(BaseModel):
    id: str
    filename: str
    content: str
    doc_type: str
    upload_date: datetime
    metadata: dict
    
class DocumentResponse(BaseModel):
    document_id: str
    answer: str
    citation: str
    
class Theme(BaseModel):
    name: str
    description: str
    supporting_documents: List[DocumentResponse]
    
class ChatResponse(BaseModel):
    themes: List[Theme]
    raw_responses: List[DocumentResponse]
