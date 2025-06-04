from typing import Optional
from jose import jwt, JWTError
from app.core.config import settings
from app.db.schemas.auth import TokenData
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException

async def generate_access_token(payload: dict, expiry: Optional[int] = None) -> TokenData:
    if expiry is None:
        expiry = settings.access_token_expiry
    
    to_encode = payload.copy()
    to_encode.update({"exp": expiry})
    encoded_jwt = jwt.encode(to_encode, settings.token_secret_key, algorithm=settings.token_algorithm)
    to_encode['exp'] = expiry * 3
    refresh_token = jwt.encode(to_encode, settings.token_secret_key, algorithm=settings.token_algorithm)
    return {"access_token": encoded_jwt, "refresh_token": refresh_token}


async def verify_access_token(token: str) -> Optional[dict]:
    try:
        decoded_jwt = jwt.decode(token, settings.token_secret_key, algorithms=[settings.token_algorithm])
        return decoded_jwt
    except JWTError:
        raise JWTError("Invalid Token")
    except Exception as e:
        print(f"An error occurred while verifying the token: {e}")
        return None
    
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(token: str = oauth2_scheme) -> dict:
    try:
        payload = await verify_access_token(token)
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")