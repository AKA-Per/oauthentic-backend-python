from sqlalchemy import events
from models.client import Client
from datetime import datetime

@events.listens_for(Client, "before_update", propagate=True)
def update_timestamp(maper, connection, target):
    target.updated_at = datetime.utcnow()

