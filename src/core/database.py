from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import get_settings
from pymongo import MongoClient
from bson.codec_options import CodecOptions
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class Database:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_db(self):
        """Create database connection."""
        try:
            # Connect with proper settings
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            self.db = self.client[settings.MONGODB_DB_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("MongoDB connection successful")
            
        except Exception as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            raise e
        
    async def close_db(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            
    async def get_collection(self, collection_name: str):
        """Get collection from database."""
        if not self.client:
            await self.connect_db()
        return self.db[collection_name]

# Create a database instance
db = Database()