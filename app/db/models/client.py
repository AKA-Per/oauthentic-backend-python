from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from app.db.models.timestampmixin import TimestampMixin

class Client(SQLModel, TimestampMixin, table=True):
    __tablename__ = "clients"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    client_id: str = Field(index=True, nullable=False, unique=True)
    name: str = Field(nullable=False)
    phone: Optional[str] = None
    email: str = Field(nullable=False, unique=True)
    access_id: str = Field(nullable=False, unique=True)
