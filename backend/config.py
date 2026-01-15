from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Spotify API credentials
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    
    # Last.fm API credentials
    lastfm_api_key: str = ""
    lastfm_api_secret: str = ""
    
    # Optional API credentials
    genius_access_token: str = ""
    discogs_token: str = ""
    youtube_api_key: str = ""
    
    # Database
    database_url: str = "sqlite:///./musicapp.db"
    
    # JWT Secret for authentication
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24 * 7  # 7 days
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

