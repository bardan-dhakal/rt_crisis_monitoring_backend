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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

logger = logging.getLogger(__name__)

class WebScraperCollector(BaseDataCollector):
    """Collector that scrapes crisis-related news from various news sources"""

    NEWS_SOURCES = [
        {
            'name': 'Test Source',
            'url': 'file://test',  # Special marker for test file
            'article_selector': 'article',
            'title_selector': 'h2',
            'link_selector': 'a',
            'is_dynamic': False
        },
        {
            'name': 'Relief Web',
            'url': 'https://reliefweb.int/updates',
            'article_selector': '.rw-river-article',
            'title_selector': '.rw-river-article__title',
            'link_selector': '.rw-river-article__title a',
            'is_dynamic': False  # Relief Web uses server-side rendering
        },
        {
            'name': 'AP News World',
            'url': 'https://apnews.com/hub/world-news',
            'article_selector': '.PageList-items-item',
            'title_selector': '.PagePromo-title',
            'link_selector': '.Link[href^="https://apnews.com/article"]',
            'is_dynamic': True  # AP News uses JavaScript to load content
        }
    ]

    def __init__(self):
        super().__init__()
        self.session = None

    async def __aenter__(self):
        await self._init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None

    async def validate_credentials(self) -> bool:
        """No credentials needed for web scraping"""
        return True

    async def _init_session(self):
        """Initialize aiohttp session if not already done"""
        if not self.session:
            try:
                self.session = aiohttp.ClientSession()
                logger.info("Initialized aiohttp session")
            except Exception as e:
                logger.error(f"Failed to initialize aiohttp session: {e}")
                raise

    async def _fetch_page(self, url: str) -> str:
        """Fetch a page and return its HTML content"""
        if url == 'file://test':
            # Read local test file
            try:
                with open('data/test_news.html', 'r') as f:
                    content = f.read()
                    logger.info("Successfully read test news file")
                    return content
            except Exception as e:
                logger.error(f"Error reading test file: {e}")
                return ""

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        try:
            logger.info(f"Attempting to fetch {url}")
            async with self.session.get(url, headers=headers, timeout=30) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {url}: HTTP {response.status}")
                    return ""
                content = await response.text()
                logger.info(f"Successfully fetched {url}, content length: {len(content)}")
                return content
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}", exc_info=True)
            return ""

    def _extract_crisis_type(self, title: str) -> EventType:
        """Determine crisis type based on keywords in title"""
        lower_title = title.lower()
        
        if any(word in lower_title for word in ['earthquake', 'tsunami', 'volcano', 'seismic']):
            return EventType.EARTHQUAKE
        elif any(word in lower_title for word in ['flood', 'hurricane', 'storm', 'tornado']):
            return EventType.FLOOD
        elif any(word in lower_title for word in ['fire', 'wildfire', 'blaze']):
            return EventType.FIRE
        elif any(word in lower_title for word in ['war', 'conflict', 'attack', 'violence', 'crisis']):
            return EventType.VIOLENCE
        elif any(word in lower_title for word in ['epidemic', 'pandemic', 'outbreak', 'disease', 'infection']):
            return EventType.DISEASE_OUTBREAK
        elif any(word in lower_title for word in ['collapse', 'infrastructure', 'power outage', 'blackout']):
            return EventType.INFRASTRUCTURE_FAILURE
        elif any(word in lower_title for word in ['protest', 'demonstration', 'riot']):
            return EventType.PROTEST
        elif any(word in lower_title for word in ['accident', 'explosion', 'spill', 'leak']):
            return EventType.INDUSTRIAL_ACCIDENT
        else:
            return EventType.OTHER

    def _get_dynamic_content(self, url: str) -> str:
        """Get content from JavaScript-rendered pages using Selenium."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info(f"Starting to fetch dynamic content from {url}")
            
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            content = driver.page_source
            logger.info(f"Successfully fetched dynamic content from {url}")
            return content
        except Exception as e:
            logger.error(f"Error fetching dynamic content from {url}: {e}", exc_info=True)
            return ""
        finally:
            try:
                driver.quit()
            except:
                pass

    async def _scrape_source(self, source: dict) -> List[CrisisEvent]:
        """Scrape a single news source for crisis-related content"""
        logger.info(f"Starting to scrape {source['name']}")
        is_dynamic = source.get("is_dynamic", False)
        
        if is_dynamic:
            html = self._get_dynamic_content(source['url'])
        else:
            html = await self._fetch_page(source['url'])

        if not html:
            logger.warning(f"No content retrieved from {source['name']}")
            return []

        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.select(source['article_selector'])
        logger.info(f"Found {len(articles)} articles on {source['name']}")

        if len(articles) == 0:
            # Log the first 200 characters of HTML for debugging
            logger.debug(f"HTML snippet from {source['name']}: {html[:200]}")
            logger.debug(f"Using article selector: {source['article_selector']}")

        crisis_events = []
        crisis_indicators = {'emergency', 'crisis', 'disaster', 'outbreak', 'earthquake', 
                           'flood', 'hurricane', 'evacuation', 'casualties', 'damage',
                           'victims', 'injured', 'dead', 'killed', 'destroyed', 'urgent',
                           'emergency', 'humanitarian', 'rescue', 'relief'}

        for i, article in enumerate(articles):
            try:
                title_elem = article.select_one(source['title_selector'])
                link_elem = article.select_one(source['link_selector'])
                
                logger.debug(f"Article {i + 1} found: Title element exists: {title_elem is not None}, Link element exists: {link_elem is not None}")
                
                if not title_elem or not link_elem:
                    logger.debug(f"Missing elements in article {i + 1}. Article HTML: {str(article)[:200]}")
                    continue

                title = title_elem.text.strip()
                link = link_elem.get('href', '')
                logger.debug(f"Processing article: {title[:100]}")

                description = article.find('p')
                description_text = description.text.strip() if description else ""
                
                # Make relative URLs absolute
                if link.startswith('/'):
                    link = f"{source['url'].split('/')[0]}//{source['url'].split('/')[2]}{link}"

                # Check both title and description for crisis indicators
                combined_text = f"{title.lower()} {description_text.lower()}"
                if any(indicator in combined_text for indicator in crisis_indicators):
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
                    logger.info(f"Found crisis event: {title}")
            except Exception as e:
                logger.error(f"Error processing article from {source['name']}: {e}")
                continue

        logger.info(f"Found {len(crisis_events)} crisis events from {source['name']}")
        return crisis_events

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Closed aiohttp session")

    async def collect(self) -> List[CrisisEvent]:
        """Collect crisis-related news from all configured sources"""
        if not self.session:
            await self._init_session()
        try:
            all_events = []
            for source in self.NEWS_SOURCES:
                try:
                    logger.info(f"Processing source: {source['name']}")
                    events = await self._scrape_source(source)
                    logger.info(f"Found {len(events)} events from {source['name']}")
                    all_events.extend(events)
                except Exception as e:
                    logger.error(f"Error processing source {source['name']}: {e}", exc_info=True)
                    continue

            logger.info(f"Collection complete. Found {len(all_events)} total events from {len(self.NEWS_SOURCES)} sources")
            return all_events

        except Exception as e:
            logger.error(f"Error in web scraping collection: {e}", exc_info=True)
            return []
        finally:
            if self.session:
                await self.session.close()
                self.session = None