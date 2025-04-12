# rt_crisis_monitoring_backend
Project Name: CrisisCopilot

Description:
CrisisCopilot is a real-time, LLM-powered emergency event monitoring system that scrapes tweets and news headlines from the internet to detect and structure information about critical situations that may require humanitarian aid or first responder intervention. This includes natural disasters (earthquakes, floods), fires, violence, disease outbreaks, infrastructure collapse, protests, accidents, and more.

The backend uses Gemini API to:

Classify whether a piece of text (tweet or headline) is related to an emergency event.

Determine event type, urgency, and affected location using natural language understanding.

Cluster texts that describe the same event based on type, location, and timestamp.

Summarize and structure the grouped event into a consistent format containing:

Event type

Location

Casualty/displacement estimates

Urgency level

Humanitarian needs

Recommended response actions

The structured information is stored in MongoDB Atlas. Each event record includes the original source texts, structured response data, and metadata for future filtering or retrieval.

The system also integrates FAISS (or Chroma) to allow for semantic vector search of similar past events, aiding NGOs and response teams with reference scenarios.

The frontend is built with Streamlit, showing:

A live feed of detected critical events

Their structured summaries

Recommended response actions

Search and filtering by location, event type, or urgency

The entire application is deployed and protected through Cloudflare, providing SSL, domain management, and DDoS protection.

Key Technologies:

Gemini API (Google) for LLM classification and structuring

LangChain for chaining LLM calls

MongoDB Atlas for event data storage

FAISS/Chroma for vector search

Streamlit for frontend dashboard

Tweepy / News API for data scraping

Cloudflare for deployment and domain security