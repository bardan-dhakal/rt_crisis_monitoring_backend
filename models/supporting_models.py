from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from models.enums import EventType, UrgencyLevel, CrisisStatus

class Location(BaseModel):
    """Structured location information for crisis events."""
    country: str
    city: Optional[str] = None
    region: Optional[str] = None
    coordinates: Optional[tuple[float, float]] = Field(
        None, 
        description="Latitude and longitude coordinates"
    )
    address: Optional[str] = None

class HumanitarianNeeds(BaseModel):
    """Represents the humanitarian needs for a crisis event."""
    medical_aid: bool = False
    shelter: bool = False
    food_water: bool = False
    rescue_teams: bool = False
    evacuation: bool = False
    infrastructure_repair: bool = False
    details: Optional[str] = None
    
class ImpactAssessment(BaseModel):
    """Assessment of the crisis impact on population and infrastructure."""
    casualties: Optional[int] = Field(None, description="Number of confirmed casualties")
    injuries: Optional[int] = Field(None, description="Number of confirmed injuries")
    displaced_people: Optional[int] = Field(None, description="Number of displaced people")
    affected_population: Optional[int] = Field(None, description="Estimated affected population")
    infrastructure_damage: Optional[str] = Field(None, description="Description of infrastructure damage")

class Source(BaseModel):
    """Source information for crisis events."""
    type: str = Field(..., description="Type of source (tweet, news, etc)")
    url: Optional[str] = None
    text: str = Field(..., description="Original text content")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(default_factory=dict)

class EventQuery(BaseModel):
    """Query parameters for filtering and sorting crisis events.
    
    This model defines all possible query parameters that can be used to filter and sort crisis events.
    It supports pagination, date range filtering, location filtering, and various sorting options.
    
    Examples:
        Query recent earthquakes:
        ```python
        EventQuery(
            event_type=EventType.EARTHQUAKE,
            sort_by="timestamp",
            sort_order="desc",
            limit=10
        )
        ```
    """
    event_type: Optional[EventType] = None
    urgency_level: Optional[UrgencyLevel] = None
    status: Optional[CrisisStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    country: Optional[str] = None
    sort_by: Optional[str] = Field(None, description="Field to sort by (timestamp, urgency_level, event_type)")
    sort_order: Optional[str] = Field("desc", description="Sort order (asc or desc)")
    limit: Optional[int] = Field(10, description="Number of events to return", ge=1, le=100)
    skip: Optional[int] = Field(0, description="Number of events to skip", ge=0)