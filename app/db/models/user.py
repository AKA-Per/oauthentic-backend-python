from typing import Optional, Union
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from app.db.models.timestampmixin import TimestampMixin
from app.types.enums import UserType

class User(SQLModel, TimestampMixin, table=True):
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    client_id: Union[UUID, None] = Field(default=None, nullable=True, index=True, foreign_key="clients.id")
    email: Union[str, None] = Field(default=None, nullable=True, unique=True)
    phone: Union[str, None] = Field(default=None, nullable=True)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    user_type: UserType = Field(default=UserType.USER)
    