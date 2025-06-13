from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.middleware.auth_middleware import verify_user
from app.db.schemas.app import CreateApp, AppBase, CreateAppData, GenerateAppCredsRequest
from app.services.app import create_app, generate_app_creds, get_all_apps, get_app_by_id
from app.utils.common import slugify, generate_string
from app.utils._logging import logger
from app.types.enums import UserType
from app.middleware.permission_middleware import has_permission
from typing import List

router = APIRouter(prefix="/app", tags=["app"])

@router.post("/")
async def create_new_app(data: CreateApp, db: AsyncSession = Depends(get_db), 
                         session_data = Depends(verify_user), 
                         dependencies = [Depends(has_permission("create_app"))]) -> AppBase:
    try:
        print(session_data)
        app_data = CreateAppData(
            **data.model_dump(),
            app_slug=slugify(data.app_name),
            app_id=generate_string(32),
            app_secret=generate_string(64),
            client_id=session_data.get('user').client_id,
            user_id=session_data.get('user').id
        )
        app = await create_app(db=db, data=app_data)
        await db.commit()
        await db.refresh(app)
        return app
    except Exception as e:
        raise e
    

@router.post("/regenerate-creds")
async def regenerate_app_creds(data: GenerateAppCredsRequest, db: AsyncSession = Depends(get_db), 
                               session = Depends(verify_user), 
                               dependencies = [Depends(has_permission("update_app"))]) -> AppBase:
    print(dependencies)
    try:
        app = await generate_app_creds(db, session.get('user').id, data.id, data.type)
        return app
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

@router.get("/")
async def get_apps(db: AsyncSession = Depends(get_db), session = Depends(verify_user), dependencies = [Depends(has_permission("view_app"))]) -> List[AppBase]:
    try:
        return await get_all_apps(db, session.get('user').id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    


@router.get("/{id}")
async def get_one_app(id: str, db: AsyncSession = Depends(get_db), session = Depends(verify_user), dependencies = [Depends(has_permission("view_app"))]) -> AppBase:
    return get_app_by_id(db, id, session.get('user').id)


