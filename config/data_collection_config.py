from typing import List, Dict

# Keywords for filtering crisis-related content
CRISIS_KEYWORDS = {
    "natural_disaster": [
        "earthquake", "flood", "hurricane", "tsunami", "tornado",
        "wildfire", "landslide", "volcanic eruption", "severe storm",
        "flash flood", "drought", "avalanche"
    ],
    "human_conflict": [
        "bombing", "shooting", "explosion", "attack", "terrorism",
        "hostage", "riot", "armed conflict", "violence", "mass shooting",
        "civil unrest"
    ],
    "health_crisis": [
        "outbreak", "epidemic", "pandemic", "mass casualty",
        "hospital emergency", "toxic spill", "disease outbreak",
        "public health emergency", "medical crisis"
    ],
    "infrastructure": [
        "building collapse", "bridge collapse", "train derailment",
        "plane crash", "major accident", "infrastructure failure",
        "power outage", "gas leak", "structural failure"
    ],
    "humanitarian": [
        "evacuation", "refugees", "humanitarian crisis",
        "emergency response", "disaster relief", "rescue operation",
        "missing people", "casualties", "stranded", "emergency shelter"
    ]
}

# Hashtags to track on Twitter/X
CRISIS_HASHTAGS = [
    "#emergency", "#disaster", "#crisis", "#breaking",
    "#rescue", "#alert", "#emergency", "#breakingnews",
    "#disaster", "#SOS", "#urgenthelp", "#911", "#firstresponders",
    "#evacuation", "#relief", "#naturaldisaster"
]

# News categories to monitor
NEWS_CATEGORIES = [
    "disasters",
    "emergencies",
    "accidents",
    "public safety",
    "weather",
    "health",
    "conflict"
]

# Minimum confidence score for LLM classification
MIN_CRISIS_CONFIDENCE = 0.6  # Lowered to catch more potential events

# Rate limiting settings (requests per minute)
RATE_LIMITS = {
    "twitter": 450,  # Twitter API v2 rate limit
    "news_api": 100,
    "rss_feeds": 30
}

# Time settings
UPDATE_INTERVAL_SECONDS = 60  # Temporarily reduced to 1 minute for testing
LOOKBACK_HOURS = 24  # How far back to look for updates