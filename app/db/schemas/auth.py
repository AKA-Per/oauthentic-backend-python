from sqlmodel import SQLModel
from uuid import UUID
from typing import Optional


class TokenData(SQLModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str = ""
    
    

class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    

class TokenRefreshRequest(SQLModel):
    refresh_token: str
    

class TokenRequest(SQLModel):
    username: str
    password: str
    


class TokenPayload(SQLModel):
    sub: UUID
    user_type: str
    session_id: str
    
class SessionPayload(SQLModel):
    user_id: UUID
    user_type: str
    device: str
    ip_address: str
    location: str
    user_agent: str