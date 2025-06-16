from sqlmodel import SQLModel
from  pydantic import EmailStr
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
    

class OAuthAppInitiate(SQLModel):
    app_id: str
    code_verifier: str
    state: str
    ip_address: str
    

class OAuthBody(SQLModel):
    code_verifier: str
    state: str
    
class UserRegister(SQLModel):
    username: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None