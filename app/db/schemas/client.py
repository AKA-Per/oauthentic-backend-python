from typing import Optional
from sqlmodel import SQLModel
from uuid import UUID
from datetime import datetime

class ClientBase(SQLModel):
    client_id: str
    name: str
    phone: Optional[str] = None
    email: str
    access_id: str
    
# class ClientCreate(ClientBase):
#     pass

class ClientRead(ClientBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        form_attributes = True
        

class ClientCreateDTO(SQLModel):
    name: str
    phone: Optional[str] = None
    email: str
    password: str
    first_name: str
    last_name: str
    
class ClientCreate(SQLModel):
    name: str
    phone: Optional[str] = None
    email: str
    client_id: str
    access_id: str