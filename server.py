from fastapi import FastAPI, Depends
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.api.v1 import clients, auth, app as app_route
import os


app = FastAPI()

@app.get("/")
async def read_root(db: AsyncSession = Depends(get_db)):
    query = text("SELECT 1")
    result = await db.execute(query, execution_options={"debug": True})
    return {"result": "OK"}

app.include_router(clients.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(app_route.router, prefix="/api/v1")
variable = 10

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="server:app", host="localhost", port=int(os.environ.get("PORT")), log_level="info", reload=True)