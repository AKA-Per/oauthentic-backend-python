from sqlmodel import SQLModel, Field
from typing import Optional, Union
from app.db.models.timestampmixin import TimestampMixin
from uuid import UUID, uuid4
from datetime import datetime


class OAuthSession(SQLModel, TimestampMixin, table=True):
    __tablename__ = "oauth_sessions"
    
    id: UUID = Field( default_factory=uuid4, primary_key=True)
    state: str = Field(nullable=False)
    code_verifier: str = Field(nullable=False)
    app_id: UUID = Field(foreign_key="apps.id", nullable=False)
    client_id: UUID = Field(foreign_key="clients.id", nullable=False)
    user_id: Union[UUID, None] = Field(foreign_key="users.id", nullable=True, default=None)
    session_id: str = Field(nullable=False)
    ip_address: str = Field(nullable=True, default=None)
    code: str = Field(nullable=True, default=None)
    expired_at: datetime = Field(nullable=False)
    is_active: bool = Field(default=True)
    