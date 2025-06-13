from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from app.db.models.auth import Auth
from app.core.security.password import hash_password, verify_password
from app.db.models.session import Session
from datetime import datetime
from datetime import timezone
from app.utils.common import generate_session_id
from app.db.schemas.auth import SessionPayload, OAuthAppInitiate

async def create_auth(db: AsyncSession, user_id: UUID, client_id: UUID, username: str, password: str):
    hashed_pw = hash_password(password)
    auth = Auth(user_id=user_id, client_id=client_id, username=username, password=hashed_pw)
    db.add(auth)
    # await db.commit()
    # await db.refresh(auth)
    return auth

async def get_auth_by_username(db: AsyncSession, username: str) -> Optional[Auth]:
    statement = select(Auth).where(Auth.username == username)
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def authenticate_user(db: AsyncSession, username: str, password: str):
    auth = await get_auth_by_username(db, username)
    if not auth:
        return None
    if not verify_password(password, auth.password):
        return None
    return auth

async def create_login_session(db: AsyncSession, payload: SessionPayload):
    session_payload = Session(
        **payload.model_dump(),
        logged_in=True,
        logged_in_at=datetime.now(timezone.utc).replace(tzinfo=None),
        last_activity=datetime.now(timezone.utc).replace(tzinfo=None),
        session_id=generate_session_id(),
    )
    db.add(session_payload)
    # await db.commit()
    # await db.refresh()
    return session_payload

async def get_session_by_id(db: AsyncSession, session_id: str) -> Optional[Session]:
    session = await db.execute(select(Session).where(Session.id == session_id))
    return session.scalar_one_or_none()

async def logout_session(db: AsyncSession, session: Session):
    # session = await get_session_by_id(db, session_id)
    session.logged_out_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.logged_in = False
    await db.commit()
    await db.refresh(session)
    

async def initiate_oauth_session(db: AsyncSession, data: OAuthAppInitiate):
    # Check the app id and app secret
    
    # From the code verfier and state create a session
    # Create a temporary token from the app secret
    # Encrypt the token and send back the session id
    # With the session id the user will redirect to the auth domain
    pass



