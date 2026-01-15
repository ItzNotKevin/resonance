import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Will import audio_analyzer when needed to avoid circular imports
_audio_analyzer = None

def get_audio_analyzer():
    global _audio_analyzer
    if _audio_analyzer is None:
        try:
            from audio_analyzer import audio_analyzer
            _audio_analyzer = audio_analyzer
        except ImportError:
            logger.warning("audio_analyzer not available (librosa not installed)")
            _audio_analyzer = False
    return _audio_analyzer if _audio_analyzer is not False else None


class SpotifyClient:
    def __init__(self):
        if not settings.spotify_client_id or not settings.spotify_client_secret:
            logger.warning("Spotify credentials not set. Please configure SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env")
            self.client = None
        else:
            try:
                auth_manager = SpotifyClientCredentials(
                    client_id=settings.spotify_client_id,
                    client_secret=settings.spotify_client_secret
                )
                self.client = spotipy.Spotify(auth_manager=auth_manager)
            except Exception as e:
                logger.error(f"Failed to initialize Spotify client: {e}")
                self.client = None
    
    def search_tracks(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for tracks by song name or artist"""
        if not self.client:
            return []
        
        try:
            results = self.client.search(q=query, type='track', limit=limit)
            tracks = []
            
            for item in results['tracks']['items']:
                track = {
                    'id': item['id'],
                    'name': item['name'],
                    'artist': ', '.join([artist['name'] for artist in item['artists']]),
                    'album': item['album']['name'],
                    'image_url': item['album']['images'][0]['url'] if item['album']['images'] else None,
                    'preview_url': item['preview_url'],  # No Deezer lookup - only fetch for recommendations
                    'popularity': item['popularity'],
                    'release_date': item['album']['release_date'],
                    'artist_ids': [artist['id'] for artist in item['artists']]
                }
                
                tracks.append(track)
            
            return tracks
        except Exception as e:
            logger.error(f"Error searching tracks: {e}")
            return []
    
    def get_track(self, track_id: str) -> Optional[Dict]:
        """Get detailed information about a track"""
        if not self.client:
            return None
        
        try:
            track = self.client.track(track_id)
            return {
                'id': track['id'],
                'name': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'preview_url': track['preview_url'],
                'popularity': track['popularity'],
                'release_date': track['album']['release_date'],
                'artist_ids': [artist['id'] for artist in track['artists']]
            }
        except Exception as e:
            logger.error(f"Error getting track {track_id}: {e}")
            return None
    
    def get_audio_features(self, track_id: str) -> Optional[Dict]:
        """
        Get audio features using FEATURE FUSION
        Combines data from multiple sources for maximum accuracy!
        """
        if not self.client:
            return None
        
        # Get track info
        track_info = self.get_track(track_id)
        if not track_info:
            return None
        
        try:
            # Use Feature Fusion system - tries all sources and combines them!
            from feature_fusion import feature_fusion
            
            features = feature_fusion.get_fused_features(
                track_name=track_info['name'],
                artist_name=track_info['artist'],
                preview_url=track_info.get('preview_url'),
                track_id=track_id
            )
            
            # Remove metadata fields
            features.pop('_sources_used', None)
            features.pop('_num_sources', None)
            
            return features
            
        except Exception as e:
            logger.error(f"Feature fusion failed for {track_id}: {e}")
            
            # Ultimate fallback: Return neutral defaults
            return {
                'acousticness': 0.5,
                'danceability': 0.5,
                'energy': 0.5,
                'instrumentalness': 0.5,
                'liveness': 0.1,
                'loudness': -10.0,
                'speechiness': 0.1,
                'tempo': 120.0,
                'valence': 0.5,
                'duration_ms': track_info.get('duration_ms', 200000) if isinstance(track_info, dict) else 200000,
                'key': 0
            }
    
    def get_artist_genres(self, artist_id: str) -> List[str]:
        """Get genres for an artist"""
        if not self.client:
            return []
        
        try:
            artist = self.client.artist(artist_id)
            return artist.get('genres', [])
        except Exception as e:
            logger.error(f"Error getting artist genres for {artist_id}: {e}")
            return []
    
    def get_recommendations(self, seed_tracks: List[str] = None, seed_artists: List[str] = None, limit: int = 50) -> List[Dict]:
        """Get Spotify's native recommendations"""
        if not self.client:
            return []
        
        try:
            recommendations = self.client.recommendations(
                seed_tracks=seed_tracks[:5] if seed_tracks else None,
                seed_artists=seed_artists[:5] if seed_artists else None,
                limit=limit
            )
            
            tracks = []
            for item in recommendations['tracks']:
                track = {
                    'id': item['id'],
                    'name': item['name'],
                    'artist': ', '.join([artist['name'] for artist in item['artists']]),
                    'album': item['album']['name'],
                    'image_url': item['album']['images'][0]['url'] if item['album']['images'] else None,
                    'preview_url': item['preview_url'],
                    'popularity': item['popularity'],
                    'release_date': item['album']['release_date'],
                    'artist_ids': [artist['id'] for artist in item['artists']]
                }
                tracks.append(track)
            
            return tracks
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    def get_related_artists(self, artist_id: str) -> List[str]:
        """Get related artist IDs"""
        if not self.client:
            return []
        
        try:
            related = self.client.artist_related_artists(artist_id)
            return [artist['id'] for artist in related['artists']]
        except Exception as e:
            logger.error(f"Error getting related artists for {artist_id}: {e}")
            return []


# Global instance
spotify_client = SpotifyClient()

