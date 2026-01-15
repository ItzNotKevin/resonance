from typing import List, Dict, Optional, Tuple
from spotify_client import spotify_client
from lastfm_client import lastfm_client
from database import SessionLocal, SwipeHistory, UserPreferences
import logging
from simple_math import (
    cosine_similarity as cosine_sim_math,
    euclidean_similarity as euclidean_sim_math,
    manhattan_similarity as manhattan_sim_math,
    mean,
    variance
)

logger = logging.getLogger(__name__)

# Feature importance weights (research-backed)
FEATURE_WEIGHTS = {
    'energy': 1.5,
    'valence': 1.5,
    'danceability': 1.3,
    'tempo': 1.2,
    'acousticness': 1.0,
    'instrumentalness': 0.9,
    'speechiness': 0.8,
    'liveness': 0.7,
    'loudness': 1.0,
    'key': 0.6,
    'duration_ms': 0.5
}

FEATURE_NAMES = list(FEATURE_WEIGHTS.keys())


def normalize_audio_features(features: Dict) -> List[float]:
    """Normalize audio features to 0-1 range - Pure Python version with robust error handling"""
    normalized = {}
    
    # Most features are already 0-1
    for key in ['acousticness', 'danceability', 'energy', 'instrumentalness', 
                'liveness', 'speechiness', 'valence']:
        val = features.get(key, 0.5)
        try:
            normalized[key] = float(val) if val is not None else 0.5
            normalized[key] = max(0.0, min(1.0, normalized[key]))
        except:
            normalized[key] = 0.5
    
    # Normalize loudness (-60 to 0 dB typical range)
    try:
        loudness = float(features.get('loudness', -30))
        normalized['loudness'] = (loudness + 60) / 60
        normalized['loudness'] = max(0, min(1, normalized['loudness']))
    except:
        normalized['loudness'] = 0.5
    
    # Normalize tempo (40-200 BPM typical range)
    try:
        tempo = float(features.get('tempo', 120))
        normalized['tempo'] = (tempo - 40) / 160
        normalized['tempo'] = max(0, min(1, normalized['tempo']))
    except:
        normalized['tempo'] = 0.5
    
    # Normalize key (0-11)
    try:
        key = features.get('key', 0)
        if isinstance(key, str):
            # Handle string keys
            key = 0
        normalized['key'] = float(key) / 11
    except:
        normalized['key'] = 0.0
    
    # Normalize duration (30s to 10min typical range)
    try:
        duration = float(features.get('duration_ms', 200000))
        normalized['duration_ms'] = (duration - 30000) / (600000 - 30000)
        normalized['duration_ms'] = max(0, min(1, normalized['duration_ms']))
    except:
        normalized['duration_ms'] = 0.5
    
    # Return as ordered list
    return [normalized[name] for name in FEATURE_NAMES]


def apply_feature_weights(features: List[float], custom_weights: Optional[Dict] = None) -> List[float]:
    """Apply importance weights to features - Pure Python version"""
    weights = FEATURE_WEIGHTS.copy()
    
    if custom_weights:
        for key, value in custom_weights.items():
            if key in weights:
                weights[key] = value
    
    weight_list = [weights[name] for name in FEATURE_NAMES]
    return [f * w for f, w in zip(features, weight_list)]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate cosine similarity (0-1, higher is more similar)"""
    return cosine_sim_math(vec_a, vec_b)


def euclidean_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate euclidean similarity (0-1, higher is more similar)"""
    return euclidean_sim_math(vec_a, vec_b)


def manhattan_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate Manhattan (L1) similarity (0-1, higher is more similar)"""
    return manhattan_sim_math(vec_a, vec_b)


def jaccard_similarity(set_a: List[str], set_b: List[str]) -> float:
    """Calculate Jaccard similarity for tags/genres"""
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
    # Max difference of 50 years
    return max(0, 1 - (year_diff / 50))


def calculate_popularity_adjustment(popularity: int) -> float:
    """Adjust score based on popularity sweet spot"""
    # Boost songs in "sweet spot" (40-70% popularity)
    # Slight penalty for extremely popular (>90%) or obscure (<10%)
    if 40 <= popularity <= 70:
        return 1.0
    elif popularity > 90:
        return 0.7  # Avoid obvious recommendations
    elif popularity < 10:
        return 0.8  # Avoid too obscure
    else:
        return 0.9


def extract_year_from_date(date_str: str) -> int:
    """Extract year from release date string"""
    try:
        return int(date_str.split('-')[0])
    except:
        return 2020  # Default to recent year


def calculate_similarity_score(
    track_features: Dict,
    seed_features: Dict,
    track_metadata: Dict,
    seed_metadata: Dict,
    user_weights: Optional[Dict] = None
) -> float:
    """Calculate comprehensive similarity score"""
    
    # Normalize features
    track_vec = normalize_audio_features(track_features)
    seed_vec = normalize_audio_features(seed_features)
    
    # Apply weights
    track_vec_weighted = apply_feature_weights(track_vec, user_weights)
    seed_vec_weighted = apply_feature_weights(seed_vec, user_weights)
    
    # Feature-based similarities (45% total)
    cos_sim = cosine_similarity(track_vec_weighted, seed_vec_weighted)
    euc_sim = euclidean_similarity(track_vec_weighted, seed_vec_weighted)
    man_sim = manhattan_similarity(track_vec_weighted, seed_vec_weighted)
    feature_score = 0.27 * cos_sim + 0.11 * euc_sim + 0.07 * man_sim
    
    # Tag/Genre similarity (20%)
    # Combine all tags: Spotify genres, Last.fm tags, AND enhanced tags from multiple APIs
    tags_seed = (seed_metadata.get('genres', []) + 
                 seed_metadata.get('lastfm_tags', []) + 
                 seed_metadata.get('enhanced_tags', []))
    tags_track = (track_metadata.get('genres', []) + 
                  track_metadata.get('lastfm_tags', []) + 
                  track_metadata.get('enhanced_tags', []))
    jaccard_sim = jaccard_similarity(tags_seed, tags_track)
    
    # Community wisdom (30%) - Increased weight for Last.fm!
    lastfm_score = track_metadata.get('lastfm_similarity', 0.0)
    
    # Contextual bonuses (5%)
    temporal_bonus = calculate_temporal_similarity(
        seed_metadata.get('release_year', 2020),
        track_metadata.get('release_year', 2020)
    )
    popularity_bonus = calculate_popularity_adjustment(track_metadata.get('popularity', 50))
    
    # Combined score
    final_score = (
        0.45 * feature_score +
        0.20 * jaccard_sim +
        0.30 * lastfm_score +
        0.025 * temporal_bonus +
        0.025 * popularity_bonus
    )
    
    return final_score


def get_user_preference_weights(user_id: int) -> Optional[Dict]:
    """Load user's learned preference weights from database"""
    db = SessionLocal()
    try:
        prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
        if prefs and prefs.feature_weights:
            return prefs.feature_weights
        return None
    finally:
        db.close()


def get_rejected_song_ids(user_id: int) -> List[str]:
    """Get list of songs user has rejected"""
    db = SessionLocal()
    try:
        rejected = db.query(SwipeHistory).filter(
            SwipeHistory.user_id == user_id,
            SwipeHistory.direction == 'left'
        ).all()
        return [swipe.song_id for swipe in rejected]
    finally:
        db.close()


def get_liked_song_ids(user_id: int) -> List[str]:
    """Get list of song IDs that user has liked (swiped right on)"""
    db = SessionLocal()
    try:
        liked = db.query(SwipeHistory).filter(
            SwipeHistory.user_id == user_id,
            SwipeHistory.direction == 'right'
        ).all()
        return [swipe.song_id for swipe in liked]
    finally:
        db.close()


def get_liked_song_keys(user_id: int) -> set:
    """Get set of song name+artist combinations that user has liked (for duplicate detection)"""
    db = SessionLocal()
    try:
        liked = db.query(SwipeHistory).filter(
            SwipeHistory.user_id == user_id,
            SwipeHistory.direction == 'right'
        ).all()
        # Return set of "song_name|artist_name" keys (lowercased)
        return {f"{swipe.song_name.lower().strip()}|{swipe.artist_name.lower().strip()}" for swipe in liked}
    finally:
        db.close()


def get_recommendations(seed_id: str, user_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
    """
    Get personalized recommendations for a seed track
    """
    logger.info(f"Getting recommendations for seed {seed_id}, user {user_id}")
    
    # 1. Fetch seed track information
    seed_track = spotify_client.get_track(seed_id)
    if not seed_track:
        logger.error(f"Could not fetch seed track {seed_id}")
        return []
    
    seed_features = spotify_client.get_audio_features(seed_id)
    if not seed_features:
        logger.error(f"Could not fetch audio features for {seed_id}")
        return []
    
    # 2. Build seed metadata
    seed_genres = []
    for artist_id in seed_track['artist_ids']:
        seed_genres.extend(spotify_client.get_artist_genres(artist_id))
    
    seed_lastfm_tags = lastfm_client.get_track_tags(
        seed_track['artist'],
        seed_track['name']
    )
    
    # Get enhanced metadata from additional APIs (TheAudioDB, Genius, Discogs, Musixmatch)
    try:
        from additional_apis import get_enhanced_metadata
        enhanced_meta = get_enhanced_metadata(seed_track['artist'], seed_track['name'])
        seed_enhanced_tags = enhanced_meta.get('enhanced_tags', [])
        logger.info(f"✅ Got {len(seed_enhanced_tags)} enhanced tags for seed")
    except Exception as e:
        logger.debug(f"Enhanced metadata fetch failed: {e}")
        seed_enhanced_tags = []
    
    seed_metadata = {
        'genres': seed_genres,
        'lastfm_tags': seed_lastfm_tags,
        'enhanced_tags': seed_enhanced_tags,
        'release_year': extract_year_from_date(seed_track['release_date']),
        'popularity': seed_track['popularity']
    }
    
    # 3. Get candidate tracks
    candidates = []
    
    # Note: Spotify removed the recommendations endpoint, so we rely entirely on Last.fm
    # and search-based discovery
    
    # From Last.fm similar tracks (PRIMARY SOURCE since Spotify recommendations are gone!)
    lastfm_similar = lastfm_client.get_similar_tracks(
        seed_track['artist'],
        seed_track['name'],
        limit=50  # Increased since this is our main source now
    )
    
    logger.info(f"Got {len(lastfm_similar)} similar tracks from Last.fm")
    
    # Search Spotify for Last.fm suggestions
    for sim_track in lastfm_similar:
        search_query = f"{sim_track['track']} {sim_track['artist']}"
        search_results = spotify_client.search_tracks(search_query, limit=1)
        if search_results:
            track = search_results[0]
            track['lastfm_similarity'] = sim_track['similarity_score']
            candidates.append(track)
    
    # Add more candidates by searching for same genres (since Spotify recommendations are gone)
    if seed_genres and len(candidates) < 30:
        logger.info("Adding genre-based candidates to supplement Last.fm")
        for genre in seed_genres[:3]:  # Top 3 genres
            genre_search = spotify_client.search_tracks(f"genre:{genre}", limit=10)
            for track in genre_search:
                if track['id'] != seed_id:
                    track['lastfm_similarity'] = 0.3  # Lower score for genre matches
                    candidates.append(track)
    
    # Add tracks from same artist (since Related Artists endpoint is gone)
    logger.info("Adding tracks from same artist")
    artist_search = spotify_client.search_tracks(f"artist:{seed_track['artist']}", limit=10)
    for track in artist_search:
        if track['id'] != seed_id:
            track['lastfm_similarity'] = 0.5  # Medium score for same artist
            candidates.append(track)
    
    # Remove duplicates AND apply diversity filter to ensure variety
    seen_ids = set()
    seen_songs = set()  # Track song name + artist combinations to prevent duplicate songs
    seen_artists = {}  # Track how many songs per artist
    unique_candidates = []
    
    # Get seed artist for comparison
    seed_artist_name = seed_track['artist'].lower()
    seed_song_key = f"{seed_track['name'].lower().strip()}|{seed_artist_name}"
    
    MAX_SAME_ARTIST = 8  # Maximum 8 songs from seed artist (they're often most similar!)
    MAX_PER_ARTIST = 3   # Maximum 3 songs from any other artist (ensures variety)
    
    # Get liked songs info for filtering (if user_id provided)
    liked_ids = set()
    liked_song_keys = set()
    if user_id:
        liked_ids = set(get_liked_song_ids(user_id))
        liked_song_keys = get_liked_song_keys(user_id)
    
    for track in candidates:
        # Skip if already seen by ID, is seed, or already liked
        if track['id'] in seen_ids or track['id'] == seed_id or track['id'] in liked_ids:
            continue
        
        artist_name = track['artist'].lower()
        song_name = track['name'].lower().strip()
        song_key = f"{song_name}|{artist_name}"
        
        # Skip if same song name + artist (different versions/albums of same song)
        # Also skip if user has already liked this song (by name+artist)
        if song_key in seen_songs or song_key == seed_song_key or song_key in liked_song_keys:
            logger.debug(f"Skipping duplicate/already-liked song: {track['name']} by {track['artist']}")
            continue
        
        # Apply diversity limits
        if artist_name == seed_artist_name:
            if seen_artists.get(artist_name, 0) >= MAX_SAME_ARTIST:
                continue  # Too many from seed artist
        else:
            if seen_artists.get(artist_name, 0) >= MAX_PER_ARTIST:
                continue  # Too many from this artist
        
        # Add track
        seen_ids.add(track['id'])
        seen_songs.add(song_key)  # Track by name+artist to prevent duplicates
        seen_artists[artist_name] = seen_artists.get(artist_name, 0) + 1
        unique_candidates.append(track)
    
    logger.info(f"Found {len(unique_candidates)} unique candidate tracks with diversity filter")
    logger.info(f"Artists represented: {len(seen_artists)} different artists")
    
    # 4. Load user preferences
    user_weights = None
    rejected_ids = []
    liked_ids = []
    liked_song_keys = set()
    if user_id:
        user_weights = get_user_preference_weights(user_id)
        rejected_ids = get_rejected_song_ids(user_id)
        liked_ids = get_liked_song_ids(user_id)
        liked_song_keys = get_liked_song_keys(user_id)
        logger.info(f"User {user_id}: {len(rejected_ids)} rejected, {len(liked_ids)} liked songs")
    
    # 5. Calculate similarity scores for all candidates
    scored_tracks = []
    for track in unique_candidates:
        # Skip rejected tracks or already-liked tracks
        if track['id'] in rejected_ids or track['id'] in liked_ids:
            continue
        
        # Also check by song name + artist (in case of different track IDs for same song)
        artist_name = track['artist'].lower()
        song_name = track['name'].lower().strip()
        song_key = f"{song_name}|{artist_name}"
        if song_key in liked_song_keys:
            logger.debug(f"Skipping already-liked song: {track['name']} by {track['artist']}")
            continue
        
        # Get audio features
        features = spotify_client.get_audio_features(track['id'])
        if not features:
            continue
        
        # Build metadata
        genres = []
        for artist_id in track.get('artist_ids', []):
            genres.extend(spotify_client.get_artist_genres(artist_id))
        
        lastfm_tags = lastfm_client.get_track_tags(track['artist'], track['name'])
        
        # Get enhanced metadata for this track too
        try:
            from additional_apis import get_enhanced_metadata
            enhanced_meta = get_enhanced_metadata(track['artist'], track['name'])
            enhanced_tags = enhanced_meta.get('enhanced_tags', [])
        except:
            enhanced_tags = []
        
        metadata = {
            'genres': genres,
            'lastfm_tags': lastfm_tags,
            'enhanced_tags': enhanced_tags,
            'release_year': extract_year_from_date(track['release_date']),
            'popularity': track['popularity'],
            'lastfm_similarity': track.get('lastfm_similarity', 0.0)
        }
        
        # Calculate similarity
        score = calculate_similarity_score(
            features,
            seed_features,
            metadata,
            seed_metadata,
            user_weights
        )
        
        scored_tracks.append({
            'id': track['id'],
            'name': track['name'],
            'artist': track['artist'],
            'album': track['album'],
            'image_url': track['image_url'],
            'preview_url': track['preview_url'],
            'audio_features': features,
            'metadata': metadata,
            'similarity_score': score
        })
    
    # 6. Sort by score
    scored_tracks.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    # 7. INTERLEAVE same-artist and discovery for engagement!
    # Pattern: 2 same-artist → 1 discovery → repeat
    seed_artist_lower = seed_track['artist'].lower()
    
    same_artist_tracks = [t for t in scored_tracks if seed_artist_lower in t['artist'].lower()]
    other_artist_tracks = [t for t in scored_tracks if seed_artist_lower not in t['artist'].lower()]
    
    logger.info(f"Interleaving: {len(same_artist_tracks)} same-artist + {len(other_artist_tracks)} discovery")
    
    interleaved = []
    same_idx = 0
    other_idx = 0
    
    while same_idx < len(same_artist_tracks) or other_idx < len(other_artist_tracks):
        # Add 2 same-artist songs (they're usually most similar!)
        for _ in range(2):
            if same_idx < len(same_artist_tracks):
                interleaved.append(same_artist_tracks[same_idx])
                same_idx += 1
        
        # Add 1 discovery song (keeps it interesting!)
        if other_idx < len(other_artist_tracks):
            interleaved.append(other_artist_tracks[other_idx])
            other_idx += 1
    
    logger.info(f"Returning {min(limit, len(interleaved))} interleaved recommendations")
    
    return interleaved[:limit]


def update_user_preferences(user_id: int):
    """Update user preferences based on swipe history"""
    db = SessionLocal()
    try:
        # Get all swipes for this user
        liked = db.query(SwipeHistory).filter(
            SwipeHistory.user_id == user_id,
            SwipeHistory.direction == 'right'
        ).all()
        
        disliked = db.query(SwipeHistory).filter(
            SwipeHistory.user_id == user_id,
            SwipeHistory.direction == 'left'
        ).all()
        
        if len(liked) < 3:  # Need minimum data
            return
        
        # Calculate average features for liked songs
        liked_features = []
        liked_genres = []
        for swipe in liked:
            if swipe.audio_features:
                liked_features.append(normalize_audio_features(swipe.audio_features))
            if swipe.track_metadata and swipe.track_metadata.get('genres'):
                liked_genres.extend(swipe.track_metadata['genres'])
        
        if not liked_features:
            return
        
        # Calculate element-wise mean of liked features (pure Python)
        num_features = len(FEATURE_NAMES)
        liked_avg = [mean([feat[i] for feat in liked_features]) for i in range(num_features)]
        
        # Calculate average features for disliked songs
        disliked_features = []
        for swipe in disliked:
            if swipe.audio_features:
                disliked_features.append(normalize_audio_features(swipe.audio_features))
        
        # Calculate preference vector
        if disliked_features:
            disliked_avg = [mean([feat[i] for feat in disliked_features]) for i in range(num_features)]
            preference_vector = [liked_avg[i] - 0.3 * disliked_avg[i] for i in range(num_features)]
        else:
            preference_vector = liked_avg
        
        # Calculate adjusted feature weights based on variance in liked songs
        feature_variance = [variance([feat[i] for feat in liked_features]) for i in range(num_features)]
        
        # Features with low variance in liked songs are important
        adjusted_weights = {}
        for i, feature_name in enumerate(FEATURE_NAMES):
            base_weight = FEATURE_WEIGHTS[feature_name]
            variance_adjustment = 1.0 + (1.0 - feature_variance[i])
            adjusted_weights[feature_name] = base_weight * variance_adjustment
        
        # Get most common genres
        from collections import Counter
        genre_counts = Counter(liked_genres)
        preferred_genres = [genre for genre, count in genre_counts.most_common(10)]
        
        # Update or create preferences
        prefs = db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
        
        if prefs:
            prefs.preference_vector = preference_vector  # Already a list
            prefs.feature_weights = adjusted_weights
            prefs.preferred_genres = preferred_genres
        else:
            prefs = UserPreferences(
                user_id=user_id,
                preference_vector=preference_vector,  # Already a list
                feature_weights=adjusted_weights,
                preferred_genres=preferred_genres
            )
            db.add(prefs)
        
        db.commit()
        logger.info(f"Updated preferences for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        db.rollback()
    finally:
        db.close()

