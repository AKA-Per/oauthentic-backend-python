from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from app.types.enums import AuthType
from app.db.models.timestampmixin import TimestampMixin

class App(SQLModel, TimestampMixin, table=True):
    __tablename__ = "apps"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(default=None, nullable=False, foreign_key="users.id")
    client_id: UUID = Field(default= None, nullable=True, foreign_key="clients.id")
    app_name: str = Field(nullable=False)
    app_slug: str = Field(nullable=False)
    app_id: str = Field(nullable=False, unique=True)
    app_secret: str = Field(nullable=False)
    scope: str = Field(nullable=False)
    domain: str = Field(nullable=False)
    callback: str = Field(nullable=False)
    auth_flow: AuthType = Field(nullable=False, default=AuthType.OAUTH)
    is_active: bool = Field(default=True)
    is_deleted: bool = Field(default=False)