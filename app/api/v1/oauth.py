from fastapi import (
    HTTPException, 
    status, 
    Depends, 
    APIRouter, 
    Header, 
    Request, 
    Query,
    Response
)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth import initiate_oauth_session, get_oauth_session
from app.db.schemas.auth import OAuthBody, OAuthAppInitiate
from app.db.session import get_db
from datetime import datetime, timezone, timedelta
from app.middleware.auth_middleware import verify_user_session_cookie
from app.utils.common import generate_string
from app.services import app as AppService


router = APIRouter(prefix="/oauth", tags=["oauth"])

@router.post("/")
async def create_initiate_session(data: OAuthBody, request: Request, x_app_id: str = Header(), db: AsyncSession = Depends(get_db)):
    client_host = request.client.host
    ip = request.headers.get("x-forwarded-for")
    ip = ip.split(",")[0] if ip else client_host
    _oauth_data = OAuthAppInitiate(
        app_id=x_app_id,
        code_verifier=data.code_verifier,
        state=data.state,
        ip_address=ip
    )
    session = await initiate_oauth_session(db, _oauth_data)
    return {
        "message": "Success", 
        "error": False, 
        "data": {
            "session_id": session.session_id
        }
    }

@router.query("/verify_auth")
async def verify_oauth_session(session_id: str = Query(None), db: AsyncSession = Depends(get_db), session = Depends(verify_user_session_cookie)):
    oauth_session = await get_oauth_session(db, session_id)
    if not oauth_session:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid oauth flow.")
    # Now check if the session has expired or not
    expiry = oauth_session.expired_at
    curr_time = datetime.now(timezone.utc).replace(tzinfo=None)
    if expiry <= curr_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session expired")
    # # Now create the code for the token
    # code = generate_string(k=64)
    # oauth_session.code = code
    # oauth_session.expired_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=2)
    # await db.commit()
    # await db.refresh(oauth_session)
    return RedirectResponse(url=f"http://localhost:5371/oath/cosent/{session_id}")

@router.query("/verify_concent")
async def verfiy_oauth_concent(session_id: str = Query(None), db: AsyncSession = Depends(get_db), session = Depends(verify_user_session_cookie)):
    oauth_session = await get_oauth_session(db, session_id)
    if not oauth_session:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid oauth flow.")
    # Now check if the session has expired or not
    expiry = oauth_session.expired_at
    curr_time = datetime.now(timezone.utc).replace(tzinfo=None)
    if expiry <= curr_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session expired")
    _app = await AppService.get_app_by_id(db, oauth_session.app_id, None)
    if not _app:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid app")
    # Now create the code for the token
    code = generate_string(k=64)
    oauth_session.code = code
    oauth_session.expired_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=2)
    await db.commit()
    await db.refresh(oauth_session)
    url = f"{_app.callback}?code={code}"
    if oauth_session.state:
        url = f"{url}&state={oauth_session.state}"
    return RedirectResponse(url=url)

@router.get("/ping")
def pong():
    return {
        "message": "Pong", 
        "pingtime": datetime.now()
    }



    
    