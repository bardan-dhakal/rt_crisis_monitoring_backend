from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import logging
from services.collection_service import CollectionService
from models.crisis_event import CrisisEvent
from typing import List
from src.core.database import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get logger for this module
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CrisisCopilot API",
    description="Real-time crisis monitoring system that processes and structures emergency event information",
    version="1.0.0"
)
collection_service = CollectionService()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Root endpoint that returns basic API information and health status"""
    return {
        "name": "CrisisCopilot API",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "events": "/events",
            "status": "/status",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.on_event("startup")
async def startup_event():
    logger.info("Starting application initialization")
    try:
        # Initialize database connection
        await db.connect_db()
        logger.info("Database connection initialized")
        
        # Start collection service
        await collection_service.start_collection()
        logger.info("Collection service started")
        
        # Start the collection loop in a background task
        asyncio.create_task(collection_service.collector_manager.start_collection_loop())
        logger.info("Collection loop started in background")
    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    collection_service.stop_collection()
    await db.close_db()
    logger.info("Application shutdown complete")

@app.get("/events", response_model=List[CrisisEvent])
async def get_events():
    try:
        events = await collection_service.collect_events()
        return events
    except Exception as e:
        logger.error(f"Error getting events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def get_status():
    return collection_service.get_collection_status()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)