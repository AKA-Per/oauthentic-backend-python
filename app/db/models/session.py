from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from typing import Optional
from app.db.models.timestampmixin import TimestampMixin
from datetime import datetime

class Session(SQLModel, TimestampMixin, table=True):
    __tablename__ = "sessions"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    session_id: str = Field(default_factory=lambda: uuid4().hex, index=True)
    user_type: str = Field(default="user")
    logged_in: bool = Field(default=True)
    logged_in_at: datetime = Field(default=None, nullable=False)
    logged_out_at: datetime = Field(default=None, nullable=False)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = Field(default=None, index=False)
    ip_address: Optional[str] = Field(default=None, index=False)
    device: Optional[str] = Field(default=None, index=False)
    location: Optional[str] = Field(default=None, index=False)
    
    