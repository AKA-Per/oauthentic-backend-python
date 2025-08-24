from fastapi import (
    HTTPException, 
    status, 
    Depends, 
    APIRouter, 
    Header, 
    Request, 
    Query,
    Response,
    Body
)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth import initiate_oauth_session, get_oauth_session, get_oauth_session_by_code
from app.db.schemas.auth import OAuthBody, OAuthAppInitiate
from app.db.session import get_db
from datetime import datetime, timezone, timedelta
from app.middleware.auth_middleware import verify_user_session_cookie
from app.utils.common import generate_string, generate_code_challange
from app.core.security import token
from app.services import app as AppService
from app.services import user as UserService
from app.core.security.security import EcryptionService, EncryptAESGCM


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

@router.get("/verify_auth")
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
    return RedirectResponse(url=f"http://localhost:5173/oath/cosent/{session_id}")

@router.get("/verify_concent")
async def verfiy_oauth_consent(session_id: str = Query(None), db: AsyncSession = Depends(get_db), session = Depends(verify_user_session_cookie)):
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
    code = generate_code_challange(code_verifier=oauth_session.code_verifier)
    oauth_session.code = code
    oauth_session.expired_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=2)
    oauth_session.user_id = session.get('user').id
    await db.commit()
    await db.refresh(oauth_session)
    url = f"{_app.callback}?code={code}"
    if oauth_session.state:
        url = f"{url}&state={oauth_session.state}"
    return RedirectResponse(url=url)

async def get_oauth_token(code_verifier: str = Body(), code: str = Body(), app_id: str = Header(None), db: AsyncSession = Depends(get_db)):
    # Verify the code
    if not code_verifier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code verifier is required.")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code is inavalid.")
    
    new_code = generate_code_challange(code_verifier=code_verifier)
    if code != new_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code.")
    # fetch the user subject
    oauth_session = await get_oauth_session_by_code(db, code)
    if not oauth_session:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid oauth session.")
    
    # Check if the session has expired or not
    expiry = oauth_session.expired_at
    curr_time = datetime.now(timezone.utc).replace(tzinfo=None)
    
    if expiry <= curr_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session has expired.")
    if oauth_session.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session timed out")
    # Check the APP
    app = await AppService.get_app_by_id(db, oauth_session.app_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid App.")
    if str(oauth_session.app_id) != app_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid app id.")
    # create the token with scope
    user = await UserService.get_user(db, oauth_session.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found.")
    # Create the Token
    payload = {
        "sub": str(oauth_session.session_id),
        "iss": "oauthentic-oauth",
        "aud": str(oauth_session.id),
        "exp": (datetime.now(timezone.utc) + timedelta(minutes=60)).timestamp()
    }
    _token = token.generate_access_token(payload=payload, expiry=60*60)
    access_token = _token.access_token
    # Encrypt the token
    encrypt_service = EncryptAESGCM(key=code_verifier)
    enncrypted_token, nonce, tag = encrypt_service.encrypt(data=access_token)
    full_encrypted_data = nonce + enncrypted_token + tag
    # return the token
    return {"message": "Success", "error": False, "data": {"token": full_encrypted_data.decode(), "token_type": "Bearer", "espires_in": 3600}}

@router.get("/ping")
def pong():
    return {
        "message": "Pong", 
        "pingtime": datetime.now()
    }



    
    