import pylast
from config import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class LastFmClient:
    def __init__(self):
        if not settings.lastfm_api_key:
            logger.warning("Last.fm API key not set. Please configure LASTFM_API_KEY in .env")
            self.network = None
        else:
            try:
                self.network = pylast.LastFMNetwork(
                    api_key=settings.lastfm_api_key,
                    api_secret=settings.lastfm_api_secret if settings.lastfm_api_secret else ""
                )
            except Exception as e:
                logger.error(f"Failed to initialize Last.fm client: {e}")
                self.network = None
    
    def get_similar_tracks(self, artist: str, track: str, limit: int = 50) -> List[Dict]:
        """Get similar tracks from Last.fm"""
        if not self.network:
            return []
        
        try:
            track_obj = self.network.get_track(artist, track)
            similar = track_obj.get_similar(limit=limit)
            
            results = []
            for sim_track, score in similar:
                try:
                    results.append({
                        'artist': sim_track.artist.name,
                        'track': sim_track.title,
                        'similarity_score': float(score)
                    })
                except Exception as e:
                    logger.debug(f"Error processing similar track: {e}")
                    continue
            
            return results
        except pylast.WSError as e:
            logger.error(f"Last.fm API error for {artist} - {track}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting similar tracks: {e}")
            return []
    
    def get_track_tags(self, artist: str, track: str, limit: int = 10) -> List[str]:
        """Get tags/genres for a track"""
        if not self.network:
            return []
        
        try:
            track_obj = self.network.get_track(artist, track)
            tags = track_obj.get_top_tags(limit=limit)
            
            return [tag.item.name.lower() for tag in tags]
        except pylast.WSError as e:
            logger.debug(f"Last.fm API error getting tags for {artist} - {track}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting track tags: {e}")
            return []
    
    def get_similar_artists(self, artist: str, limit: int = 20) -> List[str]:
        """Get similar artists"""
        if not self.network:
            return []
        
        try:
            artist_obj = self.network.get_artist(artist)
            similar = artist_obj.get_similar(limit=limit)
            
            return [sim_artist.item.name for sim_artist in similar]
        except pylast.WSError as e:
            logger.error(f"Last.fm API error for artist {artist}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting similar artists: {e}")
            return []
    
    def search_track_on_lastfm(self, artist: str, track: str) -> Optional[Dict]:
        """Search and verify a track exists on Last.fm"""
        if not self.network:
            return None
        
        try:
            track_obj = self.network.get_track(artist, track)
            # Try to get playcount to verify track exists
            playcount = track_obj.get_playcount()
            return {
                'artist': artist,
                'track': track,
                'playcount': playcount
            }
        except Exception as e:
            logger.debug(f"Track not found on Last.fm: {artist} - {track}")
            return None


# Global instance
lastfm_client = LastFmClient()


