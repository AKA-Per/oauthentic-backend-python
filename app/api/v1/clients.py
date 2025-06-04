from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.schemas.client import ClientCreateDTO, ClientRead, ClientCreate
from app.services import client as client_service
from typing import List
import random
import string


router = APIRouter(prefix="/clients", tags=["clients"])

@router.post("/", response_model=ClientRead)
async def create_client(client_in: ClientCreateDTO, db: AsyncSession = Depends(get_db)):
    # Create the client id
    client_id = ''.join(random.choices(string.digits, k=8))
    # Create the access id
    access_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    # Create the client create 
    serialize_data = client_in.model_dump()
    client_db_data = ClientCreate(name=serialize_data['name'], email=serialize_data['email'], phone=serialize_data['phone'], client_id=client_id, access_id=access_id)
    client_res = await client_service.create_client(db, client_db_data)
    # TODO create user for each client
    


@router.get("/", response_model=List[ClientRead])
async def get_clients(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    clients = await client_service.get_clients(db, skip=skip, limit=limit)
    return clients


@router.get("/{client_id}", response_model=ClientRead)
async def get_client(client_id: str, db: AsyncSession = Depends(get_db)):
    client = await client_service.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


