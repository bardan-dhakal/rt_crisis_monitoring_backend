import asyncio
import logging
from typing import List, Dict, Any
from models.crisis_event import CrisisEvent
from models.supporting_models import EventQuery
from services.collectors.collector_manager import CollectorManager
from services.collectors.web_scraper_collector import WebScraperCollector
from src.core.database import db
from config.settings import get_settings
from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime

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

    def _build_query(self, query_params: EventQuery) -> Dict[str, Any]:
        """Build MongoDB query from filter parameters"""
        query = {}
        
        # Add event type filter
        if query_params.event_type:
            query["event_type"] = query_params.event_type
            
        # Add urgency level filter
        if query_params.urgency_level:
            query["urgency_level"] = query_params.urgency_level
            
        # Add status filter
        if query_params.status:
            query["status"] = query_params.status
            
        # Add date range filter
        date_query = {}
        if query_params.start_date:
            date_query["$gte"] = query_params.start_date
        if query_params.end_date:
            date_query["$lte"] = query_params.end_date
        if date_query:
            query["timestamp"] = date_query
            
        # Add location filter
        if query_params.country:
            query["location.country"] = query_params.country
            
        return query

    def _build_sort(self, query_params: EventQuery) -> List[tuple]:
        """Build MongoDB sort parameters"""
        sort_field = query_params.sort_by or "timestamp"
        sort_order = -1 if query_params.sort_order == "desc" else 1
        return [(sort_field, sort_order)]

    async def query_events(self, query_params: EventQuery) -> List[CrisisEvent]:
        """Query events with filtering and sorting"""
        if not self._running:
            raise RuntimeError("Collection service is not running")
            
        try:
            if self.events_collection is None:
                await self._init_db()
                
            # Build query and sort parameters
            query = self._build_query(query_params)
            sort = self._build_sort(query_params)
            
            # Execute query with pagination
            cursor = self.events_collection.find(query)
            cursor = cursor.sort(sort)
            cursor = cursor.skip(query_params.skip)
            cursor = cursor.limit(query_params.limit)
            
            # Convert cursor to list of events
            events = []
            async for doc in cursor:
                events.append(CrisisEvent.model_validate(doc))
                
            return events
            
        except Exception as e:
            logger.error(f"Error querying events: {e}")
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