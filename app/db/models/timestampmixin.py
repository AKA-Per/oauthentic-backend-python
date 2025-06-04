from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional

class TimestampMixin:
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    
