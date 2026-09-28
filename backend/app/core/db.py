import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

db_instance = Database()

async def connect_to_mongo():
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    try:
        db_instance.client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
        db_instance.db = db_instance.client[settings.DATABASE_NAME]
        
        # Verify connection
        await db_instance.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB.")

        # Setup indexes
        # TTL index for company_cache: 7 days (604,800 seconds)
        await db_instance.db.company_cache.create_index("scraped_at", expireAfterSeconds=604800)
        await db_instance.db.company_cache.create_index("company_name_lower", unique=True)
        await db_instance.db.sessions.create_index("created_at")
        
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}. Falling back to in-memory storage fallback mode for session testing.")
        db_instance.client = None
        db_instance.db = None

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        logger.info("MongoDB connection closed.")

def get_database() -> Optional[AsyncIOMotorDatabase]:
    return db_instance.db
