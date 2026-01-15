"""
Simplified Recommendation Engine
Works without audio features - uses genres, popularity, artist relationships, and Last.fm
"""

from typing import List, Dict, Optional
from spotify_client import spotify_client
from lastfm_client import lastfm_client
import logging

logger = logging.getLogger(__name__)


def jaccard_similarity(set_a: List[str], set_b: List[str]) -> float:
    """Calculate Jaccard similarity for genres/tags"""
    if not set_a or not set_b:
        return 0.0
    
    set_a = set([tag.lower() for tag in set_a])
    set_b = set([tag.lower() for tag in set_b])
    
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    
    return intersection / union if union > 0 else 0.0


def calculate_temporal_similarity(year_a: int, year_b: int) -> float:
    """Calculate temporal/era similarity"""
    year_diff = abs(year_a - year_b)
    return max(0, 1 - (year_diff / 50))


def calculate_popularity_similarity(pop_a: int, pop_b: int) -> float:
    """Songs with similar popularity levels"""
    diff = abs(pop_a - pop_b)
    return max(0, 1 - (diff / 100))


def get_simple_recommendations(seed_id: str, limit: int = 50) -> List[Dict]:
    """
    Get recommendations using only available data:
    - Spotify's recommendation endpoint
    - Genre matching
    - Popularity
    - Artist relationships
    - Last.fm (if available)
    """
    logger.info(f"Getting simple recommendations for {seed_id}")
    
    # 1. Get seed track info
    seed_track = spotify_client.get_track(seed_id)
    if not seed_track:
        return []
    
    # 2. Get seed genres
    seed_genres = []
    for artist_id in seed_track['artist_ids']:
        seed_genres.extend(spotify_client.get_artist_genres(artist_id))
    
    # 3. Get Last.fm tags if available
    seed_lastfm_tags = lastfm_client.get_track_tags(
        seed_track['artist'],
        seed_track['name']
    )
    
    seed_year = int(seed_track['release_date'].split('-')[0]) if 'release_date' in seed_track else 2020
    seed_pop = seed_track['popularity']
    
    # 4. Get candidates from multiple sources
    candidates = []
    
    # From Spotify recommendations (usually works!)
    spotify_recs = spotify_client.get_recommendations(
        seed_tracks=[seed_id],
        seed_artists=seed_track['artist_ids'][:2],
        limit=40
    )
    candidates.extend(spotify_recs)
    
    # From Last.fm similar tracks
    lastfm_similar = lastfm_client.get_similar_tracks(
        seed_track['artist'],
        seed_track['name'],
        limit=30
    )
    
    for sim_track in lastfm_similar[:15]:
        search_query = f"{sim_track['track']} {sim_track['artist']}"
        search_results = spotify_client.search_tracks(search_query, limit=1)
        if search_results:
            track = search_results[0]
            track['lastfm_similarity'] = sim_track['similarity_score']
            candidates.append(track)
    
    # Remove duplicates
    seen_ids = set()
    unique_candidates = []
    for track in candidates:
        if track['id'] not in seen_ids and track['id'] != seed_id:
            seen_ids.add(track['id'])
            unique_candidates.append(track)
    
    # 5. Score all candidates
    scored_tracks = []
    
    for track in unique_candidates:
        # Get genres
        genres = []
        for artist_id in track.get('artist_ids', []):
            genres.extend(spotify_client.get_artist_genres(artist_id))
        
        # Get Last.fm tags
        lastfm_tags = lastfm_client.get_track_tags(track['artist'], track['name'])
        
        # Calculate similarity components
        
        # Genre/Tag matching (50%)
        all_seed_tags = seed_genres + seed_lastfm_tags
        all_track_tags = genres + lastfm_tags
        genre_score = jaccard_similarity(all_seed_tags, all_track_tags)
        
        # Last.fm community score (25%)
        lastfm_score = track.get('lastfm_similarity', 0.0)
        
        # Temporal similarity (15%)
        track_year = int(track['release_date'].split('-')[0]) if 'release_date' in track else 2020
        temporal_score = calculate_temporal_similarity(seed_year, track_year)
        
        # Popularity similarity (10%)
        pop_score = calculate_popularity_similarity(seed_pop, track['popularity'])
        
        # Combined score
        final_score = (
            0.50 * genre_score +
            0.25 * lastfm_score +
            0.15 * temporal_score +
            0.10 * pop_score
        )
        
        scored_tracks.append({
            'id': track['id'],
            'name': track['name'],
            'artist': track['artist'],
            'album': track['album'],
            'image_url': track['image_url'],
            'preview_url': track['preview_url'],
            'similarity_score': final_score,
            'metadata': {
                'genres': genres,
                'lastfm_tags': lastfm_tags,
                'release_year': track_year,
                'popularity': track['popularity'],
                'lastfm_similarity': lastfm_score
            }
        })
    
    # Sort by score
    scored_tracks.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    logger.info(f"Returning {min(limit, len(scored_tracks))} simple recommendations")
    return scored_tracks[:limit]












