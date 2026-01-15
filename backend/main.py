from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes import search, recommendations, user, fast_recommendations
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Music Swipe Recommendation API",
    description="API for music discovery with swipe-based recommendations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router)
app.include_router(recommendations.router)
app.include_router(fast_recommendations.router)
app.include_router(user.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")


@app.get("/")
async def root():
    return {
        "message": "Music Swipe Recommendation API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "search": "/api/search?query=<song_or_artist>",
            "recommendations": "/api/recommendations",
            "swipe": "/api/swipe",
            "register": "/api/auth/register",
            "login": "/api/auth/login"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from spotify_client import spotify_client
    spotify_configured = spotify_client.client is not None
    return {
        "status": "healthy",
        "spotify_configured": spotify_configured,
        "spotify_available": spotify_configured
    }

