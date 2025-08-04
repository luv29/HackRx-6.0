from motor.motor_asyncio import AsyncIOMotorClient
from app.core import get_settings
import os

settings = get_settings()

client = AsyncIOMotorClient(settings.mongo_uri)
db = client.hackrx
file_collection = db.files
