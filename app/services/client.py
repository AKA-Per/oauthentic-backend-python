from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db.models.client import Client
from app.db.schemas.client import ClientCreate
from datetime import datetime
from typing import Union, List
import random
import string

async def create_client(db: AsyncSession, client_data: ClientCreate) -> Client:
    """Create client in the DB

    Args:
        db (AsyncSession): The database session
        client_data (ClientCreate): The client data to be created

    Returns:
        Client: The db instance of the created client
    """
   
    
    client = Client(**client_data.model_dump())
    db.add(client)
    # await db.commit()
    # await db.refresh(client)
    return client


async def get_client_by_id(db: AsyncSession, client_id: str) -> Union[Client, None]:
    result = await db.execute(select(Client).where(Client.client_id == client_id))
    return result.scalar_one_or_none()

async def get_clients(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Client]:
    result = await db.execute(select(Client).offset(skip).limit(limit))
    return result.scalars().all()

async def delete_client(db: AsyncSession, client_id: str) -> bool:
    client = await get_client_by_id(db, client_id)
    if client:
        await db.delete(client)
        await db.commit()
        return True
    return False

async def update_client(db: AsyncSession, client_id: str, client_data: ClientCreate) -> Union[Client, None]:
    client = await get_client_by_id(db, client_id)
    if client:
        for key, value in client_data.dict().items():
            setattr(client, key, value)
            
        await db.commit()
        await db.refresh(client)
        return client
    return None


async def get_client_by_email(db: AsyncSession, email: str) -> Union[Client, None]:
    result = await db.execute(select(Client).where(Client.email == email))
    return result.scalar_one_or_none()

