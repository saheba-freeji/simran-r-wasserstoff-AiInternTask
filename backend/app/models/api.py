from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    query: str

class ErrorResponse(BaseModel):
    detail: str

class HealthCheckResponse(BaseModel):
    status: str
