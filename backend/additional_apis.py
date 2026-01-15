"""
Additional Free Music APIs
Enhances recommendations with more data sources
"""

import requests
from typing import Optional, Dict, List
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


# TheAudioDB removed - requires paid subscription for real use


class GeniusClient:
    """
    Genius API - Lyrics and song metadata
    Get token: https://genius.com/api-clients
    """
    BASE_URL = "https://api.genius.com"
    
    def __init__(self):
        self.access_token = os.getenv('GENIUS_ACCESS_TOKEN')
    
    def search_song(self, artist: str, track: str) -> Optional[Dict]:
        """Search for song and analyze lyrics themes"""
        if not self.access_token:
            return None
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(
                f"{self.BASE_URL}/search",
                headers=headers,
                params={'q': f'{track} {artist}'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('response', {}).get('hits'):
                    hit = data['response']['hits'][0]
                    result = hit['result']
                    
                    # Extract themes from tags
                    tags = []
                    if 'tags' in result:
                        tags = [tag['name'].lower() for tag in result.get('tags', [])]
                    
                    # Estimate mood from title and tags
                    title_lower = result.get('title', '').lower()
                    lyrics_state = result.get('lyrics_state', '')
                    
                    # Simple mood detection from common words
                    mood_indicators = {
                        'happy': ['happy', 'joy', 'love', 'celebration', 'party', 'dance'],
                        'sad': ['sad', 'lonely', 'heartbreak', 'tears', 'miss', 'goodbye'],
                        'energetic': ['energy', 'power', 'rock', 'pump', 'hype', 'wild'],
                        'chill': ['chill', 'relax', 'calm', 'smooth', 'mellow', 'easy'],
                        'angry': ['angry', 'rage', 'fight', 'hate', 'mad', 'fury']
                    }
                    
                    detected_moods = []
                    for mood, keywords in mood_indicators.items():
                        if any(keyword in title_lower or keyword in ' '.join(tags) for keyword in keywords):
                            detected_moods.append(mood)
                    
                    return {
                        'tags': tags,
                        'moods': detected_moods,
                        'title': result.get('title'),
                        'lyrics_available': lyrics_state == 'complete',
                        'source': 'genius'
                    }
        except Exception as e:
            logger.debug(f"Genius API fetch failed: {e}")
        return None


class DiscogsClient:
    """
    Discogs API - Detailed music database
    Get token: https://www.discogs.com/settings/developers
    """
    BASE_URL = "https://api.discogs.com"
    
    def __init__(self):
        self.token = os.getenv('DISCOGS_TOKEN')
        self.user_agent = 'MusicSwipeApp/1.0'
    
    def search_release(self, artist: str, track: str) -> Optional[Dict]:
        """Search for release and get detailed genre/style info"""
        if not self.token:
            return None
        
        try:
            headers = {
                'Authorization': f'Discogs token={self.token}',
                'User-Agent': self.user_agent
            }
            
            response = requests.get(
                f"{self.BASE_URL}/database/search",
                headers=headers,
                params={
                    'q': f'{artist} {track}',
                    'type': 'release',
                    'per_page': 1
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    result = data['results'][0]
                    
                    # Discogs has very detailed genre/style taxonomy
                    genres = [g.lower() for g in result.get('genre', [])]
                    styles = [s.lower() for s in result.get('style', [])]
                    
                    return {
                        'genres': genres,
                        'styles': styles,
                        'year': result.get('year'),
                        'country': result.get('country'),
                        'format': result.get('format', []),
                        'source': 'discogs'
                    }
        except Exception as e:
            logger.debug(f"Discogs API fetch failed: {e}")
        return None


# Musixmatch removed - free tier too limited (30 requests/day)


# Global instances (only free APIs)
genius_client = GeniusClient()
discogs_client = DiscogsClient()


def get_enhanced_metadata(artist: str, track: str) -> Dict:
    """
    Fetch metadata from FREE additional APIs in parallel
    Returns combined mood, style, and genre tags from Genius and Discogs
    """
    from concurrent.futures import ThreadPoolExecutor
    
    results = {
        'moods': [],
        'styles': [],
        'genres': [],
        'tags': []
    }
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            'genius': executor.submit(genius_client.search_song, artist, track),
            'discogs': executor.submit(discogs_client.search_release, artist, track)
        }
        
        for source, future in futures.items():
            try:
                data = future.result(timeout=5)
                if data:
                    logger.info(f"✅ Got metadata from {source}")
                    
                    # Combine all tags
                    if 'moods' in data:
                        results['moods'].extend(data['moods'])
                    if 'styles' in data:
                        results['styles'].extend(data['styles'])
                    if 'genres' in data:
                        results['genres'].extend(data['genres'])
                    if 'tags' in data:
                        results['tags'].extend(data['tags'])
            except Exception as e:
                logger.debug(f"Failed to get metadata from {source}: {e}")
    
    # Remove duplicates
    results['moods'] = list(set(results['moods']))
    results['styles'] = list(set(results['styles']))
    results['genres'] = list(set(results['genres']))
    results['tags'] = list(set(results['tags']))
    
    # Combine all as additional tags for similarity matching
    all_tags = results['moods'] + results['styles'] + results['genres'] + results['tags']
    
    logger.info(f"✅ Enhanced metadata: {len(all_tags)} total tags from multiple sources")
    
    return {
        'enhanced_tags': list(set(all_tags)),  # Deduplicated
        'moods': results['moods'],
        'styles': results['styles'],
        'additional_genres': results['genres']
    }

