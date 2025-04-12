# CrisisCopilot Backend

Real-time crisis monitoring system that processes and structures emergency event information.

## Description
CrisisCopilot is a real-time, LLM-powered emergency event monitoring system that processes tweets and news headlines to detect critical situations requiring humanitarian aid or first responder intervention.

## Quick Start

### Prerequisites
- Python 3.8 or higher
- MongoDB Atlas account
- Git

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/rt_crisis_monitoring_backend.git
cd rt_crisis_monitoring_backend
```

2. Create and activate virtual environment
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
Create a `.env` file in the root directory with:
```
MONGODB_URL="your_mongodb_connection_string"
MONGODB_DB_NAME="crisis_copilot"
```

### Running the Application

1. Start the FastAPI server
```bash
uvicorn src.main:app --reload
```

2. Access the API documentation at:
- http://localhost:8000/docs
- http://localhost:8000/redoc

## API Endpoints

- `GET /`: Health check endpoint
- `GET /api/v1/events`: List crisis events
- (More endpoints coming soon)

## Project Structure
```
rt_crisis_monitoring_backend/
├── config/
│   └── settings.py         # Application configuration
├── src/
│   ├── core/
│   │   └── database.py     # Database connection
│   └── main.py            # FastAPI application
├── .env                    # Environment variables
└── README.md              # This file
```

## Technologies Used

- **FastAPI**: Web framework for building APIs
- **MongoDB Atlas**: Cloud database
- **Motor**: Async MongoDB driver
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.