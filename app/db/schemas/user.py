from sqlmodel import SQLModel
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.types.enums import UserType

class UserBase(SQLModel):
    email: str
    phone: Optional[str] = None
    first_name: str
    last_name: str
    user_type: str
    client_id: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    

class UserCreate(SQLModel):
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    first_name: str
    last_name: str
    

class UserRead(UserBase):
    id: str
    username: str
    created_at: str
    updated_at: str
    is_active: bool = True
    is_verified: bool = False
    

    class Config:
        form_attributes = True
        use_enum_values = True
    


# Update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    user_type: Optional[UserType] = None