import asyncio
import logging
from typing import List
from models.crisis_event import CrisisEvent
from services.collectors.collector_manager import CollectorManager
from services.collectors.web_scraper_collector import WebScraperCollector
from src.core.database import db
from config.settings import get_settings
from motor.motor_asyncio import AsyncIOMotorCollection

logger = logging.getLogger(__name__)
settings = get_settings()

class CollectionService:
    def __init__(self):
        self.collector_manager = CollectorManager()
        self._running = False
        self._collection_task = None
        self.events_collection: AsyncIOMotorCollection = None

    async def _init_db(self):
        """Initialize database collection"""
        try:
            if self.events_collection is None:
                self.events_collection = await db.get_collection(settings.MONGODB_EVENTS_COLLECTION)
                logger.info(f"Initialized MongoDB collection: {settings.MONGODB_EVENTS_COLLECTION}")
        except Exception as e:
            logger.error(f"Error initializing MongoDB collection: {e}")
            raise

    async def start_collection(self):
        """Start the collection service"""
        if not self._running:
            # Initialize database first
            await self._init_db()
            
            # Initialize collectors
            logger.info("Starting collection service")
            await self.collector_manager.initialize_collectors()
            
            # Create the collection loop task if it doesn't exist
            if not self._collection_task:
                self._collection_task = asyncio.create_task(
                    self.collector_manager.start_collection_loop()
                )
                logger.info("Created collection loop task")
            
            self._running = True
            logger.info("Collection service started")

    async def stop_collection(self):
        """Stop the collection service and cleanup resources"""
        if self._running:
            self.collector_manager.stop_collection()
            if self._collection_task:
                self._collection_task.cancel()
                try:
                    await self._collection_task
                except asyncio.CancelledError:
                    pass
                self._collection_task = None
            await self.collector_manager.cleanup()
            self._running = False
            logger.info("Collection service stopped")

    async def collect_events(self) -> List[CrisisEvent]:
        """Collect crisis events and store them in the database"""
        if not self._running:
            raise RuntimeError("Collection service is not running")
        
        try:
            # Ensure database connection is initialized
            if self.events_collection is None:
                await self._init_db()
            
            # Collect events from sources
            events = await self.collector_manager.collect_all()
            
            if events:
                # Convert events to dictionaries for MongoDB storage
                event_dicts = [event.model_dump(by_alias=True) for event in events]
                
                # Store events in MongoDB
                try:
                    result = await self.events_collection.insert_many(event_dicts)
                    logger.info(f"Stored {len(result.inserted_ids)} events in MongoDB")
                except Exception as e:
                    logger.error(f"Error storing events in MongoDB: {e}")
            
            return events
        except Exception as e:
            logger.error(f"Error collecting events: {e}")
            raise

    def get_collection_status(self):
        """Get the current status of the collection service"""
        return {
            "running": self._running,
            "collectors": self.collector_manager.get_status()
        }