from sqlalchemy import create_engine

from sqlmodel import SQLModel
from app.db.models.client import Client

from app.core.config import settings

# Create the database engine
engine = create_engine(settings.sync_db_uri, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)
    

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")