from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from models import RecommendationRequest, RecommendationResponse, AudioFeatures, TrackMetadata
from progressive_recommendations import get_fast_recommendations, enrich_batch_async
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["fast-recommendations"])


@router.post("/recommendations/fast")
async def get_fast_track_recommendations(
    request: RecommendationRequest,
    background_tasks: BackgroundTasks
):
    """
    Get recommendations FAST (2-3 seconds)
    Returns initial batch immediately based on Last.fm + genres
    Audio features enriched in background
    """
    if not request.seed_id:
        raise HTTPException(status_code=400, detail="seed_id is required")
    
    try:
        # Validate seed_id
        if not request.seed_id or len(request.seed_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="seed_id is required and cannot be empty")
        
        # Get quick recommendations (Last.fm + genres only)
        recommendations = get_fast_recommendations(
            seed_id=request.seed_id,
            user_id=request.user_id,
            limit=50
        )
        
        if not recommendations or len(recommendations) == 0:
            raise HTTPException(
                status_code=404, 
                detail="No recommendations found. The seed track may not exist or have similar tracks."
            )
        
        # Schedule background enrichment for first 10 tracks
        # This will run after the response is sent!
        background_tasks.add_task(
            enrich_batch_async,
            recommendations,
            batch_size=10
        )
        
        # Convert to response model
        response = []
        for rec in recommendations:
            try:
                # Use default audio features if not enriched yet
                audio_features = rec.get('audio_features') if rec.get('audio_features') else {
                    'acousticness': 0.5,
                    'danceability': 0.5,
                    'energy': 0.5,
                    'instrumentalness': 0.5,
                    'liveness': 0.1,
                    'loudness': -10.0,
                    'speechiness': 0.1,
                    'tempo': 120.0,
                    'valence': 0.5,
                    'duration_ms': 200000,
                    'key': 0
                }
                
                # Ensure all required fields exist with defaults
                response.append({
                    'id': rec.get('id', ''),
                    'name': rec.get('name', 'Unknown'),
                    'artist': rec.get('artist', 'Unknown Artist'),
                    'album': rec.get('album', 'Unknown Album'),
                    'image_url': rec.get('image_url'),
                    'preview_url': rec.get('preview_url'),
                    'audio_features': audio_features,
                    'metadata': rec.get('metadata', {}),
                    'similarity_score': rec.get('similarity_score', 0.0)
                })
            except Exception as e:
                logger.error(f"Error formatting recommendation {rec.get('id', 'unknown')}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Skip this recommendation if it can't be formatted
                continue
        
        # Check if we have any valid recommendations after formatting
        if len(response) == 0:
            logger.warning("All recommendations were filtered out during formatting")
            raise HTTPException(
                status_code=404,
                detail="No valid recommendations could be generated. Please try a different song."
            )
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        import traceback
        error_detail = str(e) if str(e) else repr(e)
        error_traceback = traceback.format_exc()
        logger.error(f"Error generating recommendations: {error_detail}\n{error_traceback}")
        # Include more details in the error message for debugging
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating recommendations: {error_detail}. Check server logs for details."
        )


@router.post("/recommendations/enrich/{track_id}")
async def enrich_specific_track(track_id: str):
    """
    Enrich a specific track with full audio features
    Frontend can call this for tracks user is about to see
    """
    try:
        from spotify_client import spotify_client
        
        track = spotify_client.get_track(track_id)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        
        # Get full audio features
        features = spotify_client.get_audio_features(track_id)
        
        return {
            'id': track_id,
            'audio_features': features,
            'enriched': True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enriching track: {str(e)}")









