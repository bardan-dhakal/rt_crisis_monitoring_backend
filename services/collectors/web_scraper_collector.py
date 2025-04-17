from typing import List, Dict, Any
from .base_collector import BaseDataCollector
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from datetime import datetime
import logging
from config.data_collection_config import CRISIS_KEYWORDS
from models.crisis_event import CrisisEvent
from models.enums import EventType, CrisisStatus, UrgencyLevel
from models.supporting_models import Location, ImpactAssessment, HumanitarianNeeds, Source

logger = logging.getLogger(__name__)

class WebScraperCollector(BaseDataCollector):
    """Collector that scrapes crisis-related news from various news sources"""

    NEWS_SOURCES = [
        {
            'name': 'Reuters World',
            'url': 'https://www.reuters.com/world',
            'article_selector': 'article',
            'title_selector': 'h3',
            'link_selector': 'a'
        },
        {
            'name': 'Relief Web',
            'url': 'https://reliefweb.int/updates',
            'article_selector': '.article-list article',
            'title_selector': 'h3',
            'link_selector': 'a'
        },
        {
            'name': 'AP News World',
            'url': 'https://apnews.com/hub/world-news',
            'article_selector': '.FeedCard',
            'title_selector': 'h3',
            'link_selector': 'a'
        }
    ]

    def __init__(self):
        super().__init__()
        self.session = None

    async def validate_credentials(self) -> bool:
        """No credentials needed for web scraping"""
        return True

    async def _init_session(self):
        """Initialize aiohttp session if not already done"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def _fetch_page(self, url: str) -> str:
        """Fetch a page and return its HTML content"""
        try:
            async with self.session.get(url) as response:
                return await response.text()
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return ""

    def _extract_crisis_type(self, title: str) -> EventType:
        """Determine crisis type based on keywords in title"""
        lower_title = title.lower()
        
        if any(word in lower_title for word in ['earthquake', 'tsunami', 'volcano']):
            return EventType.EARTHQUAKE
        elif any(word in lower_title for word in ['war', 'conflict', 'attack']):
            return EventType.VIOLENCE
        elif any(word in lower_title for word in ['epidemic', 'pandemic', 'outbreak']):
            return EventType.DISEASE_OUTBREAK
        else:
            return EventType.OTHER

    async def _scrape_source(self, source: dict) -> List[CrisisEvent]:
        """Scrape a single news source for crisis-related content"""
        html = await self._fetch_page(source['url'])
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.select(source['article_selector'])
        crisis_events = []

        for article in articles:
            try:
                title_elem = article.select_one(source['title_selector'])
                link_elem = article.select_one(source['link_selector'])
                
                if not title_elem or not link_elem:
                    continue

                title = title_elem.text.strip()
                link = link_elem.get('href', '')
                
                # Make relative URLs absolute
                if link.startswith('/'):
                    link = f"{source['url'].split('/')[0]}//{source['url'].split('/')[2]}{link}"

                # Check if the article is crisis-related
                if any(keyword.lower() in title.lower() for keyword in CRISIS_KEYWORDS):
                    crisis_event = CrisisEvent(
                        title=title,
                        event_type=self._extract_crisis_type(title),
                        urgency_level=UrgencyLevel.MEDIUM,  # Default to medium, can be refined later
                        status=CrisisStatus.ACTIVE,
                        location=Location(country="Unknown"),  # Required field, can be refined later
                        impact=ImpactAssessment(),
                        humanitarian_needs=HumanitarianNeeds(),
                        sources=[Source(
                            type="news",
                            url=link,
                            text=title,
                            timestamp=datetime.utcnow()
                        )]
                    )
                    crisis_events.append(crisis_event)
            except Exception as e:
                logger.error(f"Error processing article from {source['name']}: {e}")
                continue

        return crisis_events

    async def collect(self) -> List[CrisisEvent]:
        """Collect crisis-related news from all configured sources"""
        await self._init_session()
        try:
            tasks = [self._scrape_source(source) for source in self.NEWS_SOURCES]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_events = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error in collection: {result}")
                elif isinstance(result, list):
                    all_events.extend(result)

            logger.info(f"Collected {len(all_events)} crisis events from web sources")
            return all_events

        except Exception as e:
            logger.error(f"Error in web scraping collection: {e}")
            return []
        finally:
            if self.session:
                await self.session.close()
                self.session = None