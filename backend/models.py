from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class TrackSearchResult(BaseModel):
    id: str
    name: str
    artist: str
    album: str
    image_url: Optional[str]
    preview_url: Optional[str]
    popularity: int


class AudioFeatures(BaseModel):
    acousticness: float
    danceability: float
    energy: float
    instrumentalness: float
    liveness: float
    loudness: float
    speechiness: float
    tempo: float
    valence: float
    duration_ms: int
    key: int


class TrackMetadata(BaseModel):
    genres: List[str]
    lastfm_tags: List[str]
    release_year: int
    popularity: int
    lastfm_similarity: float = 0.0


class RecommendationRequest(BaseModel):
    seed_id: str
    user_id: Optional[int] = None


class SwipeRequest(BaseModel):
    user_id: Optional[int] = None
    song_id: str
    song_name: str
    artist_name: str
    direction: str  # 'left' or 'right'
    audio_features: Dict
    track_metadata: Dict


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int


class RecommendationResponse(BaseModel):
    id: str
    name: str
    artist: str
    album: str
    image_url: Optional[str]
    preview_url: Optional[str]
    audio_features: AudioFeatures
    metadata: TrackMetadata
    similarity_score: float

