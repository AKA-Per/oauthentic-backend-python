from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Union
from app.db.models.user import User
from uuid import UUID
from app.types.enums import UserType

async def create_user(db: AsyncSession, user: dict) -> User:
    _user = User(**user)
    db.add(_user)
    # await db.commit()
    # await db.refresh()
    return _user

async def get_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 10, user_type: Union[UserType, None] = None) -> List[User]:
    query_builder = select(User)
    if user_type:
        query_builder = query_builder.where(User.user_type == user_type)
    result = await db.execute(query_builder.offset(skip).limit(limit))
    return result.scalars().all()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.phone == phone))
    return result.scalar_one_or_none()

async def get_user_by_client_id(db: AsyncSession, client_id: Union[str, None]) -> List[User]:
    result = await db.execute(select(User).where(User.client_id == client_id))
    return result.scalars().all()


async def get_user_count(db: AsyncSession, user_type: Union[UserType, None]=None)-> int:
    query_builder = select(User).column(User.id)
    if user_type:
        query_builder = query_builder.where(User.user_type == user_type)
    result = await db.execute(query_builder)
    return result.scalars().all().count()


