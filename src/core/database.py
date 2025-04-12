from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import get_settings

settings = get_settings()

class Database:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_db(self):
        """Create database connection."""
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
        
    async def close_db(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            
    async def get_collection(self, collection_name: str):
        """Get collection from database."""
        return self.db[collection_name]

# Create a database instance
db = Database()