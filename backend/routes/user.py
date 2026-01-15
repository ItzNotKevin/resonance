from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
from models import SwipeRequest, UserRegister, UserLogin, Token
from database import get_db, User, SwipeHistory, UserPreferences
from recommendation_engine import update_user_preferences
from config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["user"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    expires = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    to_encode = {"sub": str(user_id), "exp": expires}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/auth/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Validate password
    if len(user_data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Create new user
    hashed_pwd = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        password_hash=hashed_pwd
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(new_user.id)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id
    )


@router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login existing user
    """
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create access token
    access_token = create_access_token(user.id)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id
    )


@router.post("/swipe")
async def record_swipe(swipe_data: SwipeRequest, db: Session = Depends(get_db)):
    """
    Record a user's swipe (like/dislike)
    """
    # Create swipe record
    swipe = SwipeHistory(
        user_id=swipe_data.user_id,
        song_id=swipe_data.song_id,
        song_name=swipe_data.song_name,
        artist_name=swipe_data.artist_name,
        direction=swipe_data.direction,
        audio_features=swipe_data.audio_features,
        track_metadata=swipe_data.track_metadata
    )
    
    db.add(swipe)
    db.commit()
    
    preferences_updated = False
    
    # Update user preferences if logged in and has enough swipes
    if swipe_data.user_id:
        swipe_count = db.query(SwipeHistory).filter(
            SwipeHistory.user_id == swipe_data.user_id
        ).count()
        
        # Update preferences every 10 swipes
        if swipe_count % 10 == 0 and swipe_count > 0:
            update_user_preferences(swipe_data.user_id)
            preferences_updated = True
    else:
        # For guest users, still track swipes but don't update preferences
        # Could implement session-based learning in the future
        pass
    
    return {
        "status": "success", 
        "message": "Swipe recorded",
        "preferences_updated": preferences_updated,
        "total_swipes": db.query(SwipeHistory).filter(
            SwipeHistory.user_id == swipe_data.user_id
        ).count() if swipe_data.user_id else None
    }


@router.get("/user/preferences/{user_id}")
async def get_user_preferences(user_id: int, db: Session = Depends(get_db)):
    """
    Get user's swipe statistics and preferences
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get swipe counts
    total_swipes = db.query(SwipeHistory).filter(SwipeHistory.user_id == user_id).count()
    likes = db.query(SwipeHistory).filter(
        SwipeHistory.user_id == user_id,
        SwipeHistory.direction == 'right'
    ).count()
    dislikes = db.query(SwipeHistory).filter(
        SwipeHistory.user_id == user_id,
        SwipeHistory.direction == 'left'
    ).count()
    
    # Get recent swipes
    recent = db.query(SwipeHistory).filter(
        SwipeHistory.user_id == user_id
    ).order_by(SwipeHistory.created_at.desc()).limit(10).all()
    
    recent_swipes = [
        {
            'song_name': swipe.song_name,
            'artist_name': swipe.artist_name,
            'direction': swipe.direction,
            'timestamp': swipe.created_at.isoformat() if swipe.created_at else None
        }
        for swipe in recent
    ]
    
    # Get preferences
    preferences = None
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    if prefs:
        preferences = {
            'preference_vector': prefs.preference_vector,
            'feature_weights': prefs.feature_weights,
            'preferred_genres': prefs.preferred_genres or []
        }
    
    return {
        'username': user.username,
        'total_swipes': total_swipes,
        'likes': likes,
        'dislikes': dislikes,
        'recent_swipes': recent_swipes,
        'preferences': preferences
    }


@router.delete("/user/liked-songs/{user_id}/{song_id}")
async def remove_liked_song(user_id: int, song_id: str, db: Session = Depends(get_db)):
    """
    Remove a song from liked songs by deleting the swipe record
    This removes it from liked songs but does NOT mark it as passed/rejected
    """
    import urllib.parse
    # Decode the song_id in case it was URL encoded
    song_id = urllib.parse.unquote(song_id)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find all liked swipes for this song (in case there are duplicates)
    swipes = db.query(SwipeHistory).filter(
        SwipeHistory.user_id == user_id,
        SwipeHistory.song_id == song_id,
        SwipeHistory.direction == 'right'
    ).all()
    
    if not swipes or len(swipes) == 0:
        logger.warning(f"No liked song found: user_id={user_id}, song_id={song_id}")
        # Check if song exists with different direction
        existing = db.query(SwipeHistory).filter(
            SwipeHistory.user_id == user_id,
            SwipeHistory.song_id == song_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Song found but not in liked songs. Current direction: {existing.direction}"
            )
        raise HTTPException(status_code=404, detail=f"Liked song not found for song_id: {song_id}")
    
    # Delete the swipe records (don't mark as passed, just remove from liked)
    for swipe in swipes:
        db.delete(swipe)
    
    db.commit()
    logger.info(f"Deleted {len(swipes)} liked song record(s) for user {user_id}, song {song_id}")
    
    return {
        "status": "success",
        "message": "Song removed from liked songs",
        "removed_count": len(swipes)
    }


@router.get("/user/liked-songs/{user_id}")
async def get_liked_songs(user_id: int, db: Session = Depends(get_db)):
    """
    Get all songs the user has swiped right on (liked)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all liked swipes
    liked_swipes = db.query(SwipeHistory).filter(
        SwipeHistory.user_id == user_id,
        SwipeHistory.direction == 'right'
    ).order_by(SwipeHistory.created_at.desc()).all()
    
    # Format response
    liked_songs = []
    for swipe in liked_swipes:
        metadata = swipe.track_metadata or {}
        # Ensure image_url is accessible - check multiple possible locations
        if not metadata.get('image_url') and isinstance(metadata, dict):
            # Try to extract from nested structures
            if 'album' in metadata and isinstance(metadata['album'], dict):
                if 'images' in metadata['album'] and len(metadata['album']['images']) > 0:
                    metadata['image_url'] = metadata['album']['images'][0].get('url')
        
        # Extract image_url from metadata for easier access
        image_url = None
        if isinstance(metadata, dict):
            image_url = metadata.get('image_url')
            if not image_url and 'album' in metadata:
                album = metadata.get('album')
                if isinstance(album, dict) and 'images' in album:
                    images = album.get('images')
                    if isinstance(images, list) and len(images) > 0:
                        image_url = images[0].get('url') if isinstance(images[0], dict) else None
        
        liked_songs.append({
            'id': swipe.song_id,
            'name': swipe.song_name,
            'artist': swipe.artist_name,
            'image_url': image_url,  # Add direct image_url field
            'audio_features': swipe.audio_features or {},
            'metadata': metadata,
            'swiped_at': swipe.created_at.isoformat() if swipe.created_at else None
        })
    
    return {
        'count': len(liked_songs),
        'songs': liked_songs
    }

