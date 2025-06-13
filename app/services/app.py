from app.db.models.app import App
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas.app import CreateAppData
from sqlmodel import select
from app.utils.common import generate_string
from uuid import UUID

async def create_app(db: AsyncSession, data: CreateAppData) -> App:
    app = App(
        app_name=data.app_name,
        scope=data.scope,
        domain=data.domain,
        callback=data.callback,
        client_id=data.client_id,
        user_id=data.user_id,
        app_id=data.app_id,
        app_slug=data.app_slug,
        app_secret=data.app_secret,
        auth_flow=data.auth_flow,
    )
    db.add(app)
    db.flush()
    # Commit and refesh will be done on the controller level
    return app


async def get_app_by_id(db: AsyncSession, id: str, user_id: UUID):
    res = await db.execute(select(App).where(App.id == id and App.user_id == user_id))
    return res.scalar_one_or_none()

async def get_app_by_app_id(db: AsyncSession, app_id: str):
    res = await db.execute(select(App).where(App.app_id == app_id))
    return res.scalar_one_or_none()

async def generate_app_creds(db: AsyncSession, user_id: UUID, id: str, type: str):
    app = await get_app_by_id(db, id, user_id)
    if not app:
        raise Exception("No app found.")
    if type == "app_id":
        app.app_id = generate_string(k=32)
    if type == "app_secret":
        app.app_secret = generate_string(k=64)
    if type == "both":
        app.app_id = generate_string(k=32)
        app.app_secret = generate_string(k=64)
    await db.commit()
    await db.refresh(app)
    return app
    
async def get_all_apps(db: AsyncSession, user_id: UUID):
    apps = await db.execute(select(App).where(App.user_id == user_id))
    return apps.scalars()