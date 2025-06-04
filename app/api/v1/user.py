from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app.db.session import get_db
from app.db.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user as crud_user
from app.types.enums import UserType

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserRead)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await crud_user.create_user(db, user_in)
    return user

@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[UserRead])
async def read_users(db: AsyncSession = Depends(get_db), page: int = 1, limit: int = 10, user_type: str = None):
    skip = (page - 1) * limit
    if user_type:
        user_type = UserType(user_type)
    users = await crud_user.get_users(db, skip=skip, limit=limit, user_type=user_type)
    total_users = await crud_user.get_user_count(db, user_type=user_type)
    # Construct pagination data
    return {
        "pagination": {
            "page": page,
            "per_page": limit,
            "total": total_users,
            "total_pages": (total_users + limit -1) // limit
        },
        "users": users
    }
    

@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: UUID, user_in: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await crud_user.update_user(db, user_id, user_in.dict(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    success = await crud_user.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None


