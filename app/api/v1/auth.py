from typing import Optional, Union
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.services import auth as AuthService
from app.services import user as UserService
from app.services import client as ClientService
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.schemas.client import ClientCreateDTO, ClientCreate
from app.db.schemas.auth import TokenRequest, UserRegister
import random
import string
from app.types.enums import UserType
from app.db.schemas.auth import SessionPayload
from fastapi import Header, Request
from user_agents import parse
from app.core.security.token import generate_access_token
from app.core.security.password import verify_password
from app.utils._logging import logger
from app.middleware.auth_middleware import verify_user
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/user/register")
async def register_user(data: UserRegister, request: Request, response: Response, session_id: str = Header(), user_agent: str = Header(), db: AsyncSession = Depends(get_db) ):
    # Get the session of OAuth 
    oauth_session = await AuthService.get_oauth_session(db, session_id)
    
    if not oauth_session:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No session found.")
    # Check for expiry
    expiry_date = oauth_session.expired_at
    current_timestamp = datetime.now(timezone.utc).replace(tzinfo=None)
    if expiry_date <= current_timestamp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request expired.")
    
    # Get the client id
    client_id = oauth_session.client_id    
    # get the user based on the email username, under the client id or app id
    user = await UserService.get_user_by_email(db, data.username)
    if user:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exist.")
    # TODO create user object in DB
    user_data = {
        "email": data.username,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "phone": data.phone,
        "client_id": client_id,
        "user_type": UserType.USER,
    }
    _user = await UserService.create_user(db, user=user_data)
    await db.flush()
    # create auth object
    auth_data = {
        "user_id": _user.id,
        "client_id": client_id,
        "username": data.username,
        "password": data.password
    }
    auth = await AuthService.create_auth(db, **auth_data)
    await db.flush()
    # create the user session with token and necessary things
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
    session_payload = SessionPayload(
        user_id=_user.id,
        user_type=UserType.USER,
        device=device,
        ip_address=ip,
        user_agent=user_agent_str,
        location=""
    )
    session = await AuthService.create_login_session(db, session_payload)
    await db.flush()
    await db.commit()
    await db.refresh(_user)
    await db.refresh(auth)
    await db.refresh(session)
    logger.info("User register")
    response.set_cookie(key="session_id", value=session.session_id, max_age=3600, httponly=True)
    return {"message": "Login Success", "error": False}
    

@router.post("/user/login")
async def user_login(data: TokenRequest, request: Request, response: Response, session_id: str = Header(), user_agent: str = Header(), db: AsyncSession = Depends(get_db)):
    # Check if the user exist
    user = await UserService.get_user_by_email(db, data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid username or password")
    if user.user_type != UserType.USER:
        logger.info(f"User type is not user for email: {data.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    if not user.is_active:
        logger.info("User is not active")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    
    auth = await AuthService.get_auth_by_username(db, username=data.username)
    if not auth:
        logger.info(f"Auth information not found for the user: {data.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    if not verify_password(data.password, auth.password):
        logger.info(f"Password did not match for the user f{data.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password.")
    
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
    session_payload = SessionPayload(
        user_id=user.id,
        user_type=UserType.CLIENT,
        device=device,
        ip_address=ip,
        user_agent=user_agent_str,
        location=""
    )
    session = await AuthService.create_login_session(db, session_payload)
    await db.commit()
    await db.refresh(session)
    response.set_cookie(key="session_id", value=session.session_id, max_age=3600, httponly=True)
    return {"error": False, "message": "Login successfull"}



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
    mid = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    # Create the client create 
    serialize_data = client_data.model_dump()
    client_db_data = ClientCreate(name=serialize_data['name'], email=serialize_data['email'], phone=serialize_data['phone'], client_id=client_id, access_id=access_id, mid=mid)
    # TODO check if the client already exist with the same email
    client_exist = await ClientService.get_client_by_email(db, serialize_data['email'])
    if client_exist:
        raise HTTPException(status_code=400, detail="Client with this email already exists.")
    # TODO create the client data
    client_res = await ClientService.create_client(db, client_db_data)
    await db.flush()
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
    user = await UserService.create_user(db, user=user_data)
    await db.flush()
    # TODO create the auth for the client
    auth_data = {
        "user_id": user.id,
        "client_id": client_res.id,
        "username": serialize_data['email'],
        "password": serialize_data['password'],
    }
    auth = await AuthService.create_auth(db, **auth_data)
    await db.flush()
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
    await db.flush()
    # Now commit
    await db.commit()
    await db.refresh(client_res)
    await db.refresh(user)
    await db.refresh(auth)
    await db.refresh(session)
    logger.info("All data are saved")
    # Create the token from the session and user details
    token_payload = {
        "sub": str(session.id),
        "iss": "oauthentic",
        "aud": "oauthentic_client"
    }
    logger.info(f"Token payload: {token_payload}")
    token_data = generate_access_token(token_payload)
    logger.info(f"Token data: {token_data}")
    return token_data

@router.post("/client/login")
async def client_login(auth_data: TokenRequest, request: Request,
                           user_agent:Union[str, None]=Header(default=None),  db: AsyncSession = Depends(get_db)):
    # TODO get the username and password for the client
    username = auth_data.username
    password = auth_data.password
    # TODO check if the username is exist in the user and client table
    user = await UserService.get_user_by_email(db, username)
    if not user:
        logger.info(f"User not found {username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    if not user.user_type == UserType.CLIENT:
        logger.info(f"User is not of client type {username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    # TODO create the login session and return the same
    auth = await AuthService.get_auth_by_username(db, username) 
    # Check the password
    if not auth:
        logger.info(f"Auth not found for the user {username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password") 
    # check the password
    if not verify_password(password, auth.password):
        logger.info(f"Invalid password for the user {username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    # Create the session
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
    session_payload = SessionPayload(
        user_id=user.id,
        user_type=UserType.CLIENT,
        device=device,
        ip_address=ip,
        user_agent=user_agent_str,
        location=""
    )
    session = await AuthService.create_login_session(db, session_payload)
    await db.commit()
    await db.refresh(session)
    token_payload = {
        "sub": str(session.id),
        "iss": "oauthentic",
        "aud": "oauthentic_client"
    }
    token_data = generate_access_token(token_payload)
    return token_data

@router.post("/logout")
async def logout(db: AsyncSession = Depends(get_db), session_data = Depends(verify_user)):
    session = session_data.get("session")
    await AuthService.logout_session(db, session)
    return {"message": "Logged out successfully."}

