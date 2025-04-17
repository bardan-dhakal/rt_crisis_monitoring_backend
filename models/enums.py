from enum import Enum

class EventType(str, Enum):
    """Types of crisis events that can be monitored."""
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    FIRE = "fire"
    VIOLENCE = "violence"
    DISEASE_OUTBREAK = "disease_outbreak"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    PROTEST = "protest"
    INDUSTRIAL_ACCIDENT = "industrial_accident"
    OTHER = "other"

class UrgencyLevel(str, Enum):
    """Urgency levels for crisis events."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MONITORING = "monitoring"

class CrisisStatus(str, Enum):
    """Status of a crisis event."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    MONITORING = "monitoring"
    ARCHIVED = "archived"