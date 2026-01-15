"""
Deezer API Client - Alternative to Spotify for audio features
Deezer provides BPM and some audio data without strict restrictions
"""

import requests
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class DeezerClient:
    """Deezer API client - no authentication needed for basic features!"""
    
    BASE_URL = "https://api.deezer.com"
    
    def search_track(self, query: str) -> Optional[Dict]:
        """Search for a track on Deezer"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/search",
                params={"q": query, "limit": 1}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    return data['data'][0]
            return None
        except Exception as e:
            logger.error(f"Deezer search error: {e}")
            return None
    
    def get_track_info(self, track_id: int) -> Optional[Dict]:
        """Get track information including BPM and preview URL"""
        try:
            response = requests.get(f"{self.BASE_URL}/track/{track_id}")
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Deezer track info error: {e}")
            return None
    
    def get_preview_url(self, track_name: str, artist_name: str) -> Optional[str]:
        """
        Get Deezer preview URL for a track
        Deezer provides 30-second previews for free!
        """
        try:
            query = f"{artist_name} {track_name}"
            track = self.search_track(query)
            
            if track and track.get('preview'):
                return track['preview']  # Deezer provides direct MP3 preview URLs!
            
            return None
        except Exception as e:
            logger.debug(f"Deezer preview error for {artist_name} - {track_name}: {e}")
            return None
    
    def get_audio_features_from_spotify_track(self, track_name: str, artist_name: str) -> Optional[Dict]:
        """
        Get audio features by matching Spotify track to Deezer
        Returns estimated audio features
        """
        # Search on Deezer
        query = f"{track_name} {artist_name}"
        track = self.search_track(query)
        
        if not track:
            return None
        
        # Get detailed info
        track_info = self.get_track_info(track['id'])
        
        if not track_info:
            return None
        
        # Deezer provides BPM and duration
        # We need to estimate other features based on genre and BPM
        bpm = track_info.get('bpm', 120)
        duration_ms = track_info.get('duration', 200) * 1000
        
        # Estimate energy from BPM (higher BPM = more energy generally)
        energy = min(1.0, max(0.0, (bpm - 60) / 140))
        
        # Return compatible format
        return {
            'tempo': float(bpm),
            'duration_ms': duration_ms,
            'energy': energy,
            'loudness': -8.0,  # Default
            'key': 0,  # Default
            # These we'll use neutral values for
            'acousticness': 0.5,
            'danceability': min(1.0, energy * 1.2),  # Correlates with energy
            'instrumentalness': 0.3,
            'liveness': 0.1,
            'speechiness': 0.1,
            'valence': 0.5
        }


# Global instance
deezer_client = DeezerClient()




