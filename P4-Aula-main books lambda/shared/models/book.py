from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime
import uuid

class Book(BaseModel):
    book_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: Literal['to do', 'doing', 'done', 'blocked'] = 'to do'
    priority: Literal['low', 'medium', 'high', 'critic'] = 'medium'
    position: int = 0
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    due_date: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Implement login",
                "description": "Add JWT authentication",
                "status": "doing",
                "priority": "high",
                "position": 0,
                "tags": ["backend", "security"]
            }
        }
    
    def update_timestamp(self):
        self.updated_at = datetime.utcnow().isoformat()