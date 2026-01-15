from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from models import RecommendationRequest, RecommendationResponse, AudioFeatures, TrackMetadata
from recommendation_engine import get_recommendations
from simple_recommendation_engine import get_simple_recommendations
from database import get_db

router = APIRouter(prefix="/api", tags=["recommendations"])


@router.post("/recommendations", response_model=List[RecommendationResponse])
async def get_track_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Get personalized recommendations for a seed track
    """
    if not request.seed_id:
        raise HTTPException(status_code=400, detail="seed_id is required")
    
    try:
        recommendations = get_recommendations(
            seed_id=request.seed_id,
            user_id=request.user_id,
            limit=50
        )
        
        if not recommendations:
            raise HTTPException(status_code=404, detail="No recommendations found. Please try a different song.")
        
        # Convert to response model
        response = []
        for rec in recommendations:
            response.append(
                RecommendationResponse(
                    id=rec['id'],
                    name=rec['name'],
                    artist=rec['artist'],
                    album=rec['album'],
                    image_url=rec['image_url'],
                    preview_url=rec['preview_url'],
                    audio_features=AudioFeatures(**rec['audio_features']),
                    metadata=TrackMetadata(**rec['metadata']),
                    similarity_score=rec['similarity_score']
                )
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

