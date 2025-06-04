from typing import Optional, Union
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.services import auth as AuthService
from app.services import user as UserService
from app.services import client as ClientService
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.schemas.client import ClientCreateDTO, ClientCreate
import random
import string
from app.types.enums import UserType
from app.db.schemas.auth import SessionPayload
from fastapi import Header, Request
from user_agents import parse
from app.core.security.token import generate_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/user/register")
async def register_user(db: AsyncSession = Depends(get_db) ):
    # TODO extract user create info
    # TODO get the user based on the email username, under the client id or app id
    # TODO create user object in DB
    # TODO create auth object
    # TODO create the user session with token and necessary things
    pass

@router.post("/client/register")
async def register_client (client_data: ClientCreateDTO, 
                           request: Request,
                           user_agent:Union[str, None]=Header(default=None), 
                           db: AsyncSession = Depends(get_db)):
    # extract the client data
    # Create the client id
    client_id = ''.join(random.choices(string.digits, k=8))
    # Create the access id
    access_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    # Create the client create 
    serialize_data = client_data.model_dump()
    client_db_data = ClientCreate(name=serialize_data['name'], email=serialize_data['email'], phone=serialize_data['phone'], client_id=client_id, access_id=access_id)
    # TODO check if the client already exist with the same email
    client_exist = await ClientService.get_client_by_email(db, serialize_data['email'])
    if client_exist:
        raise HTTPException(status_code=400, detail="Client with this email already exists.")
    # TODO create the client data
    client_res = await ClientService.create_client(db, client_db_data)
    # Create user with the client data
    user_data = {
        "email": serialize_data['email'],
        "first_name": serialize_data['first_name'],
        "last_name": serialize_data['last_name'],
        "phone": serialize_data['phone'],
        "client_id": client_res.id,
        "user_type": UserType.CLIENT
    }
    # Create the user
    user = await UserService.create_user(db, user_data)
    # TODO create the auth for the client
    auth_data = {
        "user_id": user.id,
        "client_id": client_res.id,
        "username": serialize_data['email'],
        "password": serialize_data['password'],
    }
    auth = await AuthService.create_auth(db, **auth_data)
    # TODO create the session and return the same
    client_host = request.client.host
    user_agent_str = user_agent
    user_agent_parsed = parse(user_agent_str)
    device = "WEB"
    if user_agent_parsed.is_mobile:
        device = "MOBILE"
    elif user_agent_parsed.is_tablet:
        device = "TABLET"
    elif user_agent_parsed.is_pc:
        device = "PC"
    
    ip = request.headers.get("x-forwarded-for")
    ip = ip.split(",")[0] if ip else client_host
    
    session_pauload = SessionPayload(
        user_id=user.id,
        user_type=UserType.CLIENT,
        device=device,
        ip_address=ip,
        user_agent=user_agent_str,
        location=""
    )
    session = await AuthService.create_login_session(db, session_pauload)
    # Create the token from the session and user details
    token_payload = {
        "sub": session.id,
        "iss": "oauthentic",
        "aud": "oauthentic_client"
    }
    token_data = generate_access_token(token_payload)
    return token_data

@router.post("/client/login")
async def client_login(db: AsyncSession = Depends(get_db)):
    # TODO get the username and password for the client
    # TODO check if the username is exist in the user and client table
    # TODO create the login session and return the same
    pass



