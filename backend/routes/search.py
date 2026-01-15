from fastapi import APIRouter, HTTPException
from typing import List
from models import TrackSearchResult
from spotify_client import spotify_client
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=List[TrackSearchResult])
async def search_tracks(query: str, limit: int = 20):
    """
    Search for tracks by song name or artist
    """
    if not query or len(query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    # Check if Spotify client is initialized
    if not spotify_client.client:
        logger.error("Spotify client not initialized. Check credentials.")
        raise HTTPException(
            status_code=503, 
            detail="Search service unavailable. Please check Spotify API credentials."
        )
    
    try:
        # Run the synchronous search in a thread pool with timeout
        loop = asyncio.get_event_loop()
        
        # Add timeout to prevent hanging
        try:
            results = await asyncio.wait_for(
                loop.run_in_executor(
                    None, 
                    lambda: spotify_client.search_tracks(query, limit=limit)
                ),
                timeout=8.0  # 8 second timeout for Spotify API call
            )
        except asyncio.TimeoutError:
            logger.error(f"Search timeout for query: {query}")
            raise HTTPException(
                status_code=504,
                detail="Search request timed out. Please try again."
            )
        
        if not results:
            logger.warning(f"No results found for query: {query}")
            return []
        
        return [
            TrackSearchResult(
                id=track['id'],
                name=track['name'],
                artist=track['artist'],
                album=track['album'],
                image_url=track['image_url'],
                preview_url=track['preview_url'],
                popularity=track['popularity']
            )
            for track in results
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching tracks: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error searching tracks: {str(e)}"
        )




