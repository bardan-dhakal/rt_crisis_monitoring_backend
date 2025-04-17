from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from models.enums import EventType, UrgencyLevel
from models.supporting_models import Location, HumanitarianNeeds, ImpactAssessment, Source
from uuid import UUID, uuid4
from bson import ObjectId

class CrisisEvent(BaseModel):
    """
    Comprehensive model for crisis events in the system.
    """
    # Identification
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    title: str = Field(..., description="Brief description of the crisis")
    
    # Classification
    event_type: EventType
    urgency_level: UrgencyLevel
    status: str = Field(default="active", description="Current status of the event")
    
    # Location and Timing
    location: Location
    timestamp: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    # Impact and Needs
    impact: ImpactAssessment
    humanitarian_needs: HumanitarianNeeds
    recommended_actions: List[str] = Field(default_factory=list)
    
    # Sources and Verification
    sources: List[Source] = Field(default_factory=list)
    verification_status: str = Field(default="unverified")
    
    # Vector Search
    embedding_vector: Optional[List[float]] = Field(
        None, 
        description="Vector embedding for similarity search"
    )
    similar_events: List[str] = Field(
        default_factory=list,
        description="IDs of similar events"
    )
    
    # Additional Information
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }