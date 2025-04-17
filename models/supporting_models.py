from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

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