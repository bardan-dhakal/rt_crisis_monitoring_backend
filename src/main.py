from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import logging
from services.collection_service import CollectionService
from models.crisis_event import CrisisEvent
from typing import List

app = FastAPI()
collection_service = CollectionService()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await collection_service.start_collection()

@app.on_event("shutdown")
def shutdown_event():
    collection_service.stop_collection()

@app.get("/events", response_model=List[CrisisEvent])
async def get_events():
    try:
        events = await collection_service.collect_events()
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def get_status():
    return collection_service.get_collection_status()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)