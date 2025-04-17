import asyncio
import logging
from typing import List
from models.crisis_event import CrisisEvent
from services.collectors.collector_manager import CollectorManager
from services.collectors.web_scraper_collector import WebScraperCollector

logger = logging.getLogger(__name__)

class CollectionService:
    def __init__(self):
        self.collector_manager = CollectorManager()
        self._running = False
        self._collection_task = None

    async def start_collection(self):
        """Start the collection service"""
        if not self._running:
            # Initialize collectors first
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
        """Collect crisis events from all registered collectors"""
        if not self._running:
            raise RuntimeError("Collection service is not running")
        
        try:
            events = await self.collector_manager.collect_all()
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