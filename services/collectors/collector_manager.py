import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
from .web_scraper_collector import WebScraperCollector
from config.data_collection_config import UPDATE_INTERVAL_SECONDS
from .base_collector import BaseDataCollector
from models.crisis_event import CrisisEvent

logger = logging.getLogger(__name__)

class CollectorManager:
    """Manages the web scraper collector for crisis monitoring"""
    
    def __init__(self):
        self.collectors: List[BaseDataCollector] = [
            WebScraperCollector()
        ]
        self.is_running = False
        self.last_run = None
        self._collection_task = None
        self.collection_count = 0

    def register_collector(self, collector: BaseDataCollector):
        """Register a new collector instance"""
        if not isinstance(collector, BaseDataCollector):
            raise ValueError("Collector must be an instance of BaseDataCollector")
        self.collectors.append(collector)
        logger.info(f"Registered new collector: {collector.__class__.__name__}")
    
    async def initialize_collectors(self) -> bool:
        """Initialize all collectors and validate their credentials"""
        logger.info("Initializing collectors")
        all_valid = True
        for collector in self.collectors:
            try:
                logger.info(f"Validating credentials for {collector.__class__.__name__}")
                is_valid = await collector.validate_credentials()
                if not is_valid:
                    logger.error(f"Failed to validate credentials for {collector.__class__.__name__}")
                    all_valid = False
            except Exception as e:
                logger.error(f"Error validating {collector.__class__.__name__}: {e}")
                all_valid = False
        return all_valid
    
    async def collect_all(self) -> List[CrisisEvent]:
        """Collect data from all collectors"""
        logger.info("Starting collection cycle from all collectors")
        all_events = []
        for collector in self.collectors:
            try:
                logger.info(f"Collecting from {collector.__class__.__name__}")
                events = await collector.collect()
                all_events.extend(events)
                self.collection_count += len(events)
                self.last_run = datetime.utcnow()
                logger.info(f"Collected {len(events)} events from {collector.__class__.__name__}")
            except Exception as e:
                logger.error(f"Error collecting from {collector.__class__.__name__}: {e}", exc_info=True)
        logger.info(f"Collection cycle complete. Found {len(all_events)} events")
        return all_events
    
    async def start_collection_loop(self):
        """Start continuous data collection loop"""
        # Reset running state when starting new loop
        self.is_running = False
        
        if self.is_running:
            logger.warning("Collection loop is already running")
            return
            
        self.is_running = True
        logger.info("Starting collection loop")
        
        while self.is_running:
            try:
                logger.info(f"Starting scheduled collection cycle at {datetime.utcnow()}")
                events = await self.collect_all()
                logger.info(f"Scheduled collection cycle completed. Found {len(events)} events")
                
                # Wait for next interval
                await asyncio.sleep(UPDATE_INTERVAL_SECONDS)
                
            except Exception as e:
                logger.error(f"Error in collection loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    async def cleanup(self):
        """Cleanup all collectors"""
        logger.info("Cleaning up collectors")
        self.is_running = False  # Stop the collection loop
        for collector in self.collectors:
            if hasattr(collector, 'cleanup'):
                try:
                    await collector.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up collector {collector.__class__.__name__}: {e}")

    def stop_collection(self):
        """Stop the collection loop"""
        logger.info("Stopping collection loop")
        self.is_running = False

    def get_status(self):
        """Get the current status of the collection process"""
        return {
            "last_collection_time": self.last_run,
            "items_collected": self.collection_count
        }

# Example usage:
# manager = CollectorManager()
# manager.add_collector(WebScraperCollector(api_key="...", ...))
# manager.add_collector(NewsCollector(api_key="..."))