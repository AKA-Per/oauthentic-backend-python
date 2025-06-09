from fastapi import Depends, HTTPException, status, Header
from app.db.session import get_db
from app.db.models.session import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security.token import verify_access_token
from typing import Union
from app.utils._logging import logger
from app.services.auth import get_session_by_id
from app.services.user import get_user


async def verify_user(authorization: Union[str, None] = Header(None), db: AsyncSession = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        logger.error("Authorization header is missing or invalid")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization.")
    token = authorization.split(" ")[1]
    payload = verify_access_token(token)
    if not payload:
        logger.error("Token decode faced some error")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
    
    session_id = payload.get("sub")
    if not session_id:
        logger.error("Session ID is missing in the token payload.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    session = await get_session_by_id(db, session_id)
    if not session:
        logger.error(f"Session with the ID {session_id} not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found.")
    if session.logged_out_at:
        logger.error(f"Session already logged out.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid.")
    
    # Get the user id
    user_id = session.user_id
    if not user_id:
        logger.error("User ID is missing from the session.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session.")
    # Fetch the user details
    user = await get_user(db, user_id)
    if not user:
        logger.error(f"User with the ID {user_id} not found.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session.")
    if not user.is_active:
        logger.error(f"User with the ID {user_id} is not active")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session.")
    
    return {"user": user, "session": session}

