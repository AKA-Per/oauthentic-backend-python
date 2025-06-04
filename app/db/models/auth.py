from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Auth(SQLModel, table=True):
    __tablename__ = "auth"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(default=None, nullable=False, foreign_key="users.id")
    client_id: UUID = Field(default= None, nullable=True, foreign_key="clients.id")
    username: str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)