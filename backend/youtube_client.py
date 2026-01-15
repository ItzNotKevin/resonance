"""
YouTube Client - Completely FREE (No API key needed!)
Uses web scraping to get YouTube URLs for song previews
"""

import requests
from typing import Optional, Dict
import logging
import re
from urllib.parse import quote

logger = logging.getLogger(__name__)


class YouTubeClient:
    """YouTube client that works WITHOUT API key - completely free!"""
    
    def __init__(self):
        # No API key needed!
        pass
    
    def search_video(self, query: str, max_results: int = 1) -> Optional[Dict]:
        """
        Search for a YouTube video using web scraping
        No API key required!
        """
        try:
            # Search YouTube using their public search
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Extract video ID from the page
                # YouTube embeds video IDs in their response
                pattern = r'"videoId":"([a-zA-Z0-9_-]{11})"'
                matches = re.findall(pattern, response.text)
                
                if matches:
                    video_id = matches[0]  # Get first result
                    return {
                        'video_id': video_id,
                        'title': query,
                        'url': f"https://www.youtube.com/watch?v={video_id}"
                    }
            
            return None
        except Exception as e:
            logger.debug(f"YouTube search error: {e}")
            return None
    
    def get_video_preview_url(self, track_name: str, artist_name: str) -> Optional[str]:
        """
        Get a YouTube video preview URL for a track
        Completely FREE - no API key needed!
        Note: Returns None for now as YouTube embeds don't work with Audio() tag
        Would need to implement YouTube IFrame API for proper playback
        """
        # TODO: Implement proper YouTube playback using IFrame API
        # For now, return None to let Spotify previews work
        return None


# Global instance
youtube_client = YouTubeClient()
