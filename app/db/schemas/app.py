from sqlmodel import SQLModel
from uuid import UUID
from typing import Optional, Union
from app.types.enums import AuthType

class AppBase(SQLModel):
    id: UUID
    user_id: UUID
    client_id: UUID
    app_name: str
    app_slug: str
    app_id: str
    app_secret: str
    scope: str
    callback: str
    domain: str
    auth_flow: AuthType
    

class CreateApp(SQLModel):
    app_name: str
    scope: str
    callback: str
    domain: str
    auth_flow: AuthType
    
    

class CreateAppData(CreateApp):
    client_id: UUID
    user_id: UUID
    app_slug: str
    app_id: str
    app_secret: str

class GenerateAppCredsRequest(SQLModel):
    id: str
    type: str