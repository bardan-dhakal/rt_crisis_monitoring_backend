import asyncio
import logging
from typing import List
from models.crisis_event import CrisisEvent
from services.collectors.collector_manager import CollectorManager
from services.collectors.web_scraper_collector import WebScraperCollector

class CollectionService:
    def __init__(self):
        self.collector_manager = CollectorManager()
        self._running = False

    async def start_collection(self):
        """Start the collection service"""
        if not self._running:
            # Initialize collectors first
            await self.collector_manager.initialize_collectors()
            # Start the collection loop
            asyncio.create_task(self.collector_manager.start_collection_loop())
            self._running = True
            logging.info("Collection service started")

    async def stop_collection(self):
        """Stop the collection service and cleanup resources"""
        if self._running:
            self.collector_manager.stop_collection()
            await self.collector_manager.cleanup()
            self._running = False
            logging.info("Collection service stopped")

    async def collect_events(self) -> List[CrisisEvent]:
        """Collect crisis events from all registered collectors"""
        if not self._running:
            raise RuntimeError("Collection service is not running")
        
        try:
            events = await self.collector_manager.collect_all()
            return events
        except Exception as e:
            logging.error(f"Error collecting events: {e}")
            raise

    def get_collection_status(self):
        """Get the current status of the collection service"""
        return {
            "running": self._running,
            "collectors": self.collector_manager.get_status()
        }