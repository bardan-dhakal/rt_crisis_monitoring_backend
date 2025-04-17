from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime, timedelta
from config.data_collection_config import CRISIS_KEYWORDS, CRISIS_HASHTAGS
from models.crisis_event import CrisisEvent

class BaseDataCollector(ABC):
    """Base class for all data collectors (Twitter, News, RSS, etc)"""
    
    def __init__(self):
        # Initialize the combined keywords list
        self.keywords = self._flatten_keywords()
        
    def _flatten_keywords(self) -> List[str]:
        """Flatten the keyword dictionary into a list"""
        keywords = []
        # Add individual keywords from each category
        for category_keywords in CRISIS_KEYWORDS.values():
            keywords.extend(category_keywords)
        
        # Add hashtags without the '#' symbol for text matching
        clean_hashtags = [tag.replace('#', '') for tag in CRISIS_HASHTAGS]
        keywords.extend(clean_hashtags)
        
        # Convert to set to remove duplicates and back to list
        unique_keywords = list(set(keywords))
        print(f"Initialized with {len(unique_keywords)} unique keywords")
        return unique_keywords
    
    def is_relevant_content(self, text: str) -> bool:
        """Check if content contains any crisis-related keywords"""
        if not text:
            return False
            
        text = text.lower()
        # Check for keywords
        for keyword in self.keywords:
            if keyword.lower() in text:
                print(f"Found relevant keyword: {keyword} in text: {text[:100]}...")
                return True
        return False
    
    @abstractmethod
    async def collect(self) -> List[CrisisEvent]:
        """Collect data from the source"""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate API credentials"""
        pass