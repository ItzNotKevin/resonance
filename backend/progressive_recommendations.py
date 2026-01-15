"""
Progressive Recommendation System
Returns recommendations quickly, enriches features in background
"""

from typing import List, Dict, Optional
from spotify_client import spotify_client
from lastfm_client import lastfm_client
from recommendation_engine import (
    calculate_similarity_score,
    extract_year_from_date,
    jaccard_similarity,
    calculate_temporal_similarity,
    calculate_popularity_adjustment
)
import logging
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)


def get_fast_recommendations(seed_id: str, user_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
    """
    Fast recommendation system - returns initial batch immediately
    Audio features enriched progressively in background
    Uses user preferences if available
    """
    logger.info(f"Getting FAST recommendations for {seed_id}, user {user_id}")
    
    # Get user preferences and rejected songs if user_id provided
    rejected_ids = set()
    liked_ids = set()
    liked_song_keys = set()
    if user_id:
        from recommendation_engine import get_rejected_song_ids, get_liked_song_ids, get_liked_song_keys
        rejected_ids = set(get_rejected_song_ids(user_id))
        liked_ids = set(get_liked_song_ids(user_id))
        liked_song_keys = get_liked_song_keys(user_id)
        logger.info(f"User {user_id} has rejected {len(rejected_ids)} songs and liked {len(liked_ids)} songs")
    
    # 1. Get seed track (fast - cached by Spotify)
    if not spotify_client.client:
        logger.error("Spotify client not initialized. Cannot get recommendations.")
        raise ValueError("Spotify client not initialized. Please check API credentials.")
    
    seed_track = spotify_client.get_track(seed_id)
    if not seed_track:
        logger.warning(f"Seed track {seed_id} not found in Spotify")
        raise ValueError(f"Seed track {seed_id} not found. Please try a different song.")
    
    # 2. Get seed metadata (fast)
    seed_genres = []
    for artist_id in seed_track['artist_ids']:
        seed_genres.extend(spotify_client.get_artist_genres(artist_id))
    
    seed_lastfm_tags = lastfm_client.get_track_tags(seed_track['artist'], seed_track['name'])
    seed_year = extract_year_from_date(seed_track['release_date'])
    seed_pop = seed_track['popularity']
    
    # 3. Get candidate tracks from Last.fm (PRIMARY SOURCE - fast!)
    logger.info("Getting candidates from Last.fm...")
    lastfm_similar = lastfm_client.get_similar_tracks(
        seed_track['artist'],
        seed_track['name'],
        limit=50
    )
    
    logger.info(f"Last.fm returned {len(lastfm_similar)} similar tracks")
    
    candidates = []
    
    # Search Spotify for Last.fm suggestions (fast - just metadata)
    # Prioritize high-similarity tracks from Last.fm
    # Only use tracks with decent Last.fm similarity (>= 0.3) to avoid unrelated songs
    MIN_LASTFM_SIMILARITY = 0.3
    high_similarity_tracks = [st for st in lastfm_similar if st.get('similarity_score', 0) >= MIN_LASTFM_SIMILARITY]
    
    logger.info(f"Last.fm returned {len(lastfm_similar)} tracks, {len(high_similarity_tracks)} with similarity >= {MIN_LASTFM_SIMILARITY}")
    
    # Use high-similarity tracks first, then fall back to others if needed
    tracks_to_search = high_similarity_tracks[:40] if len(high_similarity_tracks) >= 20 else lastfm_similar[:40]
    
    for sim_track in tracks_to_search:
        try:
            search_query = f"{sim_track['track']} {sim_track['artist']}"
            search_results = spotify_client.search_tracks(search_query, limit=1)
            if search_results:
                track = search_results[0]
                track['lastfm_similarity'] = sim_track['similarity_score']
                candidates.append(track)
        except Exception as e:
            logger.debug(f"Failed to search for {search_query}: {e}")
            continue
    
    # Add same artist tracks (increased limit for more candidates)
    try:
        artist_search = spotify_client.search_tracks(f"artist:{seed_track['artist']}", limit=50)  # Increased from 20
        same_artist_count = 0
        for track in artist_search:
            if track['id'] != seed_id:
                # Give same-artist tracks a moderate Last.fm score (0.5-0.6 range)
                # Still good but allows other tracks to compete
                track['lastfm_similarity'] = 0.6 - (same_artist_count * 0.005)  # Reduced from 0.8
                track['is_same_artist'] = True  # Flag for later use
                candidates.append(track)
                same_artist_count += 1
        logger.info(f"Added {same_artist_count} tracks from same artist: {seed_track['artist']}")
    except Exception as e:
        logger.warning(f"Failed to search for artist tracks: {e}")
    
    # Fallback: If we have very few candidates, try genre-based search
    if len(candidates) < 20:  # Increased threshold
        logger.info(f"Only {len(candidates)} candidates, trying genre-based search")
        try:
            if seed_genres:
                # Search by multiple genres for more results
                for genre in seed_genres[:3]:
                    genre_query = f"genre:{genre}"
                    genre_results = spotify_client.search_tracks(genre_query, limit=30)  # Increased from 15
                    for track in genre_results:
                        if track['id'] != seed_id:
                            track['lastfm_similarity'] = 0.3  # Lower score for genre matches
                            candidates.append(track)
        except Exception as e:
            logger.debug(f"Genre search failed: {e}")
    
    logger.info(f"Collected {len(candidates)} total candidates before deduplication")
    
    # Remove duplicates AND apply diversity filter AND filter rejected songs
    seen_ids = set()
    seen_songs = set()  # Track song name + artist combinations to prevent duplicate songs
    seen_artists = {}  # Track how many songs per artist
    unique_candidates = []
    
    # Get seed artist for comparison
    seed_artist_name = seed_track['artist'].lower()
    seed_song_key = f"{seed_track['name'].lower().strip()}|{seed_artist_name}"
    
    MAX_SAME_ARTIST = 8  # Maximum songs from seed artist (they ARE often most similar!)
    MAX_PER_ARTIST = 3   # Maximum songs from any other single artist (ensure variety)
    
    for track in candidates:
        # Skip if already seen by ID, is seed, was rejected, or was already liked by user
        if track['id'] in seen_ids or track['id'] == seed_id or track['id'] in rejected_ids or track['id'] in liked_ids:
            continue
        
        artist_name = track['artist'].lower()
        song_name = track['name'].lower().strip()
        song_key = f"{song_name}|{artist_name}"
        
        # Skip if same song name + artist (different versions/albums of same song)
        # Also skip if user has already liked this song (by name+artist)
        if song_key in seen_songs or song_key == seed_song_key or song_key in liked_song_keys:
            logger.debug(f"Skipping duplicate/already-liked song: {track['name']} by {track['artist']}")
            continue
        
        # Check artist diversity limits
        if artist_name == seed_artist_name:
            # Limit same artist as seed
            if seen_artists.get(artist_name, 0) >= MAX_SAME_ARTIST:
                continue  # Skip - too many from this artist
        else:
            # Limit other artists too
            if seen_artists.get(artist_name, 0) >= MAX_PER_ARTIST:
                continue  # Skip - too many from this artist
        
        # Add track
        seen_ids.add(track['id'])
        seen_songs.add(song_key)  # Track by name+artist to prevent duplicates
        seen_artists[artist_name] = seen_artists.get(artist_name, 0) + 1
        unique_candidates.append(track)
    
    logger.info(f"Got {len(unique_candidates)} unique candidates with diversity filter")
    logger.info(f"Artists represented: {len(seen_artists)}")
    if user_id:
        logger.info(f"Filtered out: {len(liked_ids)} liked songs by ID, {len(liked_song_keys)} by name+artist")
    
    # If we have no candidates after filtering, keep searching until we find some
    # This is a more aggressive approach - keep expanding search until we have candidates
    if len(unique_candidates) == 0:
        logger.warning("No unique candidates found after filtering! Expanding search aggressively...")
        logger.warning(f"   Total candidates before filter: {len(candidates)}")
        logger.warning(f"   Liked songs filtered: {len(liked_ids)} IDs, {len(liked_song_keys)} keys")
        logger.warning(f"   Rejected songs filtered: {len(rejected_ids)}")
        
        # Keep searching until we have at least 10 candidates or run out of options
        max_search_rounds = 5
        search_round = 0
        
        while len(unique_candidates) < 10 and search_round < max_search_rounds:
            search_round += 1
            logger.info(f"Expanded search round {search_round}...")
            
            try:
                # Round 1: More tracks from same artist (PRIORITY - these are most relevant)
                # Only use this if we have very few candidates, prioritize same-artist
                if search_round == 1:
                    expanded_artist_search = spotify_client.search_tracks(f"artist:{seed_track['artist']}", limit=100)
                    for track in expanded_artist_search:
                        if track['id'] not in seen_ids and track['id'] != seed_id:
                            # Round 1: Only allow if not liked and not rejected (strict)
                            if track['id'] not in liked_ids and track['id'] not in rejected_ids:
                                artist_name = track['artist'].lower()
                                song_name = track['name'].lower().strip()
                                song_key = f"{song_name}|{artist_name}"
                                
                                if song_key not in seen_songs and song_key != seed_song_key and song_key not in liked_song_keys:
                                    # Give same-artist tracks a good similarity score
                                    track['lastfm_similarity'] = 0.5  # Moderate score for same-artist
                                    track['is_same_artist'] = True
                                    seen_ids.add(track['id'])
                                    seen_songs.add(song_key)
                                    unique_candidates.append(track)
                                    logger.debug(f"Added expanded same-artist candidate: {track['name']} by {track['artist']}")
                
                # Round 2: Still prioritize same-artist, but allow rejected songs
                if search_round == 2:
                    expanded_artist_search = spotify_client.search_tracks(f"artist:{seed_track['artist']}", limit=100)
                    for track in expanded_artist_search:
                        if track['id'] not in seen_ids and track['id'] != seed_id:
                            # Round 2: Allow rejected songs for same-artist only
                            if track['id'] not in liked_ids:
                                artist_name = track['artist'].lower()
                                song_name = track['name'].lower().strip()
                                song_key = f"{song_name}|{artist_name}"
                                
                                if song_key not in seen_songs and song_key != seed_song_key and song_key not in liked_song_keys:
                                    track['lastfm_similarity'] = 0.4  # Lower score for rejected songs
                                    track['is_same_artist'] = True
                                    seen_ids.add(track['id'])
                                    seen_songs.add(song_key)
                                    unique_candidates.append(track)
                                    logger.debug(f"Added expanded same-artist candidate (round 2): {track['name']} by {track['artist']}")
                
                # Round 3+: Genre searches (only if we still need more)
                # Only use top genres to maintain relevance
                if search_round >= 3 and seed_genres and len(unique_candidates) < 10:
                    for genre in seed_genres[:2]:  # Only top 2 genres to maintain relevance
                        genre_search = spotify_client.search_tracks(f"genre:{genre}", limit=30)  # Reduced from 50
                        for track in genre_search:
                            if track['id'] not in seen_ids and track['id'] != seed_id:
                                # In round 3+, allow rejected songs but prioritize non-rejected
                                if track['id'] not in liked_ids:
                                    artist_name = track['artist'].lower()
                                    song_name = track['name'].lower().strip()
                                    song_key = f"{song_name}|{artist_name}"
                                    
                                    if song_key not in seen_songs and song_key != seed_song_key and song_key not in liked_song_keys:
                                        # Give genre matches a lower score
                                        track['lastfm_similarity'] = 0.25 if track['id'] in rejected_ids else 0.3
                                        seen_ids.add(track['id'])
                                        seen_songs.add(song_key)
                                        unique_candidates.append(track)
                                        logger.debug(f"Added genre candidate: {track['name']} by {track['artist']}")
                
                logger.info(f"After search round {search_round}: {len(unique_candidates)} candidates")
                
                # If we have enough candidates, break early
                if len(unique_candidates) >= 10:
                    break
                    
            except Exception as e:
                logger.error(f"Error during expanded search round {search_round}: {e}")
        
        # Final fallback: If we still have very few candidates, allow some rejected songs
        if len(unique_candidates) < 5:
            logger.warning(f"Only {len(unique_candidates)} candidates after aggressive search. Allowing some rejected songs as last resort...")
            # Re-search and allow rejected songs (but still filter liked songs)
            try:
                fallback_search = spotify_client.search_tracks(f"artist:{seed_track['artist']}", limit=100)
                for track in fallback_search:
                    if track['id'] not in seen_ids and track['id'] != seed_id and track['id'] not in liked_ids:
                        artist_name = track['artist'].lower()
                        song_name = track['name'].lower().strip()
                        song_key = f"{song_name}|{artist_name}"
                        
                        if song_key not in seen_songs and song_key != seed_song_key and song_key not in liked_song_keys:
                            seen_ids.add(track['id'])
                            seen_songs.add(song_key)
                            unique_candidates.append(track)
                            if len(unique_candidates) >= 10:
                                break
                logger.info(f"After fallback search: {len(unique_candidates)} candidates")
            except Exception as e:
                logger.error(f"Error during fallback search: {e}")
        
        # If we still have no candidates, we have a serious problem
        if len(unique_candidates) == 0:
            logger.error("Still no candidates after all search attempts!")
            logger.error("User may have liked/rejected too many songs. Cannot generate recommendations.")
            return []
    
    elif len(unique_candidates) < 3:
        logger.warning(f"Very few candidates ({len(unique_candidates)}), may not provide enough recommendations")
        logger.warning(f"   Total candidates before filter: {len(candidates)}")
        logger.warning(f"   This might be due to aggressive filtering or limited Last.fm results")
    
    # 4. Quick scoring (no audio features yet!)
    scored_tracks = []
    
    for track in unique_candidates:
        # Get basic metadata (fast - Spotify cache)
        genres = []
        for artist_id in track.get('artist_ids', []):
            genres.extend(spotify_client.get_artist_genres(artist_id))
        
        # Quick Last.fm tags (skip if slow)
        try:
            lastfm_tags = lastfm_client.get_track_tags(track['artist'], track['name'])
        except:
            lastfm_tags = []
        
        track_year = extract_year_from_date(track['release_date'])
        
        # FAST SCORING without audio features
        # Last.fm score (40% - increased weight since it's our primary source)
        lastfm_score = track.get('lastfm_similarity', 0.0)
        
        # Genre/tag matching (25% - increased weight for better relevance)
        all_seed_tags = seed_genres + seed_lastfm_tags
        all_track_tags = genres + lastfm_tags
        jaccard_sim = jaccard_similarity(all_seed_tags, all_track_tags)
        
        # Artist match bonus (12% - balanced for relevance but allows variety)
        # Still important but not overwhelming
        artist_match = 0.0
        track_artist_lower = track['artist'].lower()
        seed_artist_lower = seed_artist_name.lower()
        
        # Check for exact artist match (case-insensitive)
        if track_artist_lower == seed_artist_lower:
            artist_match = 1.0  # Same artist - full bonus
            logger.debug(f"Same artist match: {track['artist']} = {seed_track['artist']}")
        elif seed_artist_lower in track_artist_lower or track_artist_lower in seed_artist_lower:
            artist_match = 0.6  # Partial artist match (reduced from 0.8)
            logger.debug(f"Partial artist match: {track['artist']} contains {seed_track['artist']}")
        elif any(seed_genre in genres for seed_genre in seed_genres[:3] if seed_genres):
            artist_match = 0.2  # Similar genre artists - smaller bonus
        
        # Temporal (5%)
        temporal = calculate_temporal_similarity(seed_year, track_year)
        
        # Popularity (5%)
        pop_adj = calculate_popularity_adjustment(track['popularity'])
        
        # Quick score (100% - balanced for relevance AND variety)
        # Prioritize Last.fm and genre matching, moderate artist boost
        quick_score = (
            0.40 * lastfm_score +  # Increased - Last.fm is most reliable
            0.25 * jaccard_sim +   # Increased - genre matching is important
            0.12 * artist_match +  # Reduced from 20% - still important but allows variety
            0.08 * temporal +
            0.08 * pop_adj +
            0.07 * (1.0 if artist_match > 0.5 else 0.0)  # Small extra boost for same/partial artist (reduced from 15%)
        )
        
        # Log scoring breakdown for top candidates (for debugging)
        if len(scored_tracks) < 5:  # Log first few tracks
            logger.debug(f"Score breakdown for {track['name']} by {track['artist']}:")
            logger.debug(f"  Last.fm: {lastfm_score:.3f} (35%), Genre: {jaccard_sim:.3f} (20%), Artist: {artist_match:.3f} (20%+15%), Temporal: {temporal:.3f} (5%), Pop: {pop_adj:.3f} (5%)")
            logger.debug(f"  Final score: {quick_score:.3f}")
        
        # Try Deezer if Spotify doesn't have a preview (for recommendations only!)
        preview_url = track['preview_url']
        if not preview_url:
            try:
                from deezer_client import deezer_client
                deezer_url = deezer_client.get_preview_url(track['name'], track['artist'])
                if deezer_url:
                    preview_url = deezer_url
                    logger.info(f"Got Deezer preview for recommendation: {track['name']}")
            except Exception as e:
                logger.debug(f"Deezer fallback failed for {track['name']}: {e}")
        
        # Note: audio_features will be None initially
        scored_tracks.append({
            'id': track['id'],
            'name': track['name'],
            'artist': track['artist'],
            'album': track['album'],
            'image_url': track['image_url'],
            'preview_url': preview_url,  # Includes Deezer fallback
            'audio_features': None,  # Will be enriched later
            'metadata': {
                'genres': genres,
                'lastfm_tags': lastfm_tags,
                'enhanced_tags': [],
                'release_year': track_year,
                'popularity': track['popularity'],
                'lastfm_similarity': lastfm_score
            },
            'similarity_score': quick_score,
            '_needs_enrichment': True  # Flag for background processing
        })
    
    # Sort by quick score
    scored_tracks.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    # Filter out very low-quality matches
    # Increased threshold to 0.35 (35%) to ensure only relevant songs
    MIN_SIMILARITY_THRESHOLD = 0.35
    original_count = len(scored_tracks)
    filtered_tracks = [t for t in scored_tracks if t['similarity_score'] >= MIN_SIMILARITY_THRESHOLD]
    
    if len(filtered_tracks) < original_count:
        removed = original_count - len(filtered_tracks)
        logger.info(f"Filtered out {removed} tracks with similarity < {MIN_SIMILARITY_THRESHOLD} (35%)")
    
    # If we filtered out too many, lower threshold slightly but still keep it high
    if len(filtered_tracks) < 5 and original_count > 0:
        logger.warning(f"Only {len(filtered_tracks)} tracks passed 35% threshold! Lowering to 0.30 to get more results")
        MIN_SIMILARITY_THRESHOLD = 0.30
        filtered_tracks = [t for t in scored_tracks if t['similarity_score'] >= MIN_SIMILARITY_THRESHOLD]
        if len(filtered_tracks) < 3:
            logger.warning(f"Still only {len(filtered_tracks)} tracks! Lowering to 0.25")
            MIN_SIMILARITY_THRESHOLD = 0.25
            filtered_tracks = [t for t in scored_tracks if t['similarity_score'] >= MIN_SIMILARITY_THRESHOLD]
    
    scored_tracks = filtered_tracks
    
    logger.info(f"Scored {len(scored_tracks)} tracks (from {len(unique_candidates)} candidates)")
    if len(scored_tracks) > 0:
        logger.info(f"Score range: {scored_tracks[0]['similarity_score']:.3f} (top) to {scored_tracks[-1]['similarity_score']:.3f} (bottom)")
        # Log top 3 scores for debugging
        for i, track in enumerate(scored_tracks[:3], 1):
            logger.debug(f"  {i}. {track['name']} by {track['artist']}: {track['similarity_score']:.3f}")
    
    # INTERLEAVE same artist and discovery for better variety!
    # Pattern: 1 same-artist → 2 discovery → 1 same-artist → 2 discovery...
    # This ensures good variety while still including same-artist tracks
    seed_artist_lower = seed_track['artist'].lower()
    
    same_artist_tracks = [t for t in scored_tracks if seed_artist_lower in t['artist'].lower()]
    other_artist_tracks = [t for t in scored_tracks if seed_artist_lower not in t['artist'].lower()]
    
    logger.info(f"Interleaving: {len(same_artist_tracks)} same-artist + {len(other_artist_tracks)} discovery")
    
    # If we have very few tracks, just return them all (no interleaving needed)
    # But make sure we have at least a few - if only 1, something went wrong
    if len(scored_tracks) <= 5:
        logger.info(f"Few tracks available ({len(scored_tracks)}), returning all without interleaving")
        if len(scored_tracks) == 0:
            logger.error("No scored tracks available! This should not happen.")
            return []
        # Always return at least what we have, up to limit
        return scored_tracks[:limit]
    
    # Interleave: 1 same-artist → 3 discovery (aggressive variety!)
    # Also enforce: never more than 2 same-artist tracks in a row
    interleaved = []
    same_idx = 0
    other_idx = 0
    consecutive_same_artist = 0  # Track consecutive same-artist tracks
    MAX_CONSECUTIVE_SAME = 2  # Never allow more than 2 same-artist in a row
    
    # Continue until we've used all tracks or reached a reasonable limit
    max_iterations = 100  # Safety limit to prevent infinite loops
    iteration = 0
    
    while (same_idx < len(same_artist_tracks) or other_idx < len(other_artist_tracks)) and len(interleaved) < limit * 2 and iteration < max_iterations:
        iteration += 1
        
        # FORCE other-artist track if we've had too many same-artist in a row
        if consecutive_same_artist >= MAX_CONSECUTIVE_SAME:
            if other_idx < len(other_artist_tracks):
                interleaved.append(other_artist_tracks[other_idx])
                other_idx += 1
                consecutive_same_artist = 0  # Reset counter
                continue  # Skip to next iteration
            # If no other-artist tracks available, we'll add same-artist below
        
        # Add 1 same-artist song (if we haven't hit the consecutive limit)
        if same_idx < len(same_artist_tracks) and consecutive_same_artist < MAX_CONSECUTIVE_SAME:
            interleaved.append(same_artist_tracks[same_idx])
            same_idx += 1
            consecutive_same_artist += 1
        elif same_idx < len(same_artist_tracks):
            # We've hit the consecutive limit, skip this same-artist track
            same_idx += 1
            consecutive_same_artist = 0  # Reset since we're skipping
        
        # Add 3 discovery songs (increased for more variety!)
        for _ in range(3):
            if other_idx < len(other_artist_tracks):
                interleaved.append(other_artist_tracks[other_idx])
                other_idx += 1
                consecutive_same_artist = 0  # Reset counter when we add other-artist
            else:
                break
    
    logger.info(f"Interleaving complete: {len(interleaved)} tracks interleaved (same: {same_idx}/{len(same_artist_tracks)}, other: {other_idx}/{len(other_artist_tracks)})")
    
    # If we still don't have enough, add remaining tracks in order
    if len(interleaved) < limit:
        logger.warning(f"Only got {len(interleaved)} interleaved tracks, filling with remaining scored tracks")
        remaining = [t for t in scored_tracks if t not in interleaved]
        needed = limit - len(interleaved)
        interleaved.extend(remaining[:needed])
        logger.info(f"Added {min(needed, len(remaining))} remaining tracks, now have {len(interleaved)} total")
    
    # Final fallback: if we still don't have enough, return what we have
    if len(interleaved) == 0 and len(scored_tracks) > 0:
        logger.warning(f"Interleaving produced no results, returning first {limit} scored tracks")
        interleaved = scored_tracks[:limit]
    
    # Ensure we return at least what we have (up to limit)
    result = interleaved[:limit] if len(interleaved) > 0 else scored_tracks[:limit]
    
    # Safety check: if result is empty, return early
    if len(result) == 0:
        logger.warning("⚠️ No recommendations to return after interleaving!")
        return []
    
    # FORCE minimum variety: Ensure at least 50% of recommendations are from other artists
    # This prevents same-artist tracks from dominating the results
    # Also ensure we never have more than 2 same-artist tracks in a row
    if len(result) > 0 and len(other_artist_tracks) > 0:
        same_artist_in_result = [t for t in result if seed_artist_lower in t['artist'].lower()]
        other_artist_in_result = [t for t in result if seed_artist_lower not in t['artist'].lower()]
        
        min_other_artist_count = max(3, int(len(result) * 0.5))  # At least 50% or 3 tracks, whichever is higher
        
        # Check for consecutive same-artist tracks and break them up (do this first)
        MAX_CONSECUTIVE_SAME = 2
        max_iterations = 5  # Limit how many times we try to fix consecutive tracks
        iteration = 0
        while iteration < max_iterations:
            found_consecutive = False
            for i in range(len(result) - MAX_CONSECUTIVE_SAME):
                # Check if we have 3+ same-artist tracks in a row
                window = result[i:i+MAX_CONSECUTIVE_SAME+1]
                same_artist_count = sum(1 for t in window if seed_artist_lower in t['artist'].lower())
                if same_artist_count > MAX_CONSECUTIVE_SAME:
                    # Find an other-artist track to insert
                    available_other = [t for t in other_artist_tracks if t not in result]
                    if available_other:
                        # Insert an other-artist track to break up the sequence
                        result.insert(i + MAX_CONSECUTIVE_SAME, available_other[0])
                        logger.info(f"Broke up consecutive same-artist tracks by inserting {available_other[0]['name']} by {available_other[0]['artist']}")
                        found_consecutive = True
                        break  # Restart the check after insertion
            if not found_consecutive:
                break  # No more consecutive sequences found
            iteration += 1
        
        # Recalculate counts after breaking up consecutive tracks
        same_artist_in_result = [t for t in result if seed_artist_lower in t['artist'].lower()]
        other_artist_in_result = [t for t in result if seed_artist_lower not in t['artist'].lower()]
        
        if len(other_artist_in_result) < min_other_artist_count:
            logger.info(f"Forcing variety: Only {len(other_artist_in_result)} other-artist tracks, need at least {min_other_artist_count}")
            
            # Get additional other-artist tracks that aren't already in result
            available_other_artist = [t for t in other_artist_tracks if t not in result]
            
            # Calculate how many same-artist tracks to replace
            needed_other = min_other_artist_count - len(other_artist_in_result)
            can_replace = min(needed_other, len(available_other_artist), len(same_artist_in_result))
            
            if can_replace > 0:
                # Remove some same-artist tracks from the end (lowest priority)
                # and replace with other-artist tracks
                result_without_same = [t for t in result if seed_artist_lower not in t['artist'].lower()]
                same_artist_to_keep = same_artist_in_result[:-can_replace] if len(same_artist_in_result) > can_replace else []
                new_other_artist = available_other_artist[:can_replace]
                
                # Rebuild result: keep all other-artist tracks, keep remaining same-artist, add new other-artist
                result = result_without_same + same_artist_to_keep + new_other_artist
                
                # Re-sort by score to maintain quality
                result.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
                result = result[:limit]  # Trim to limit
                
                # Recalculate final counts after replacement
                final_same = len([t for t in result if seed_artist_lower in t['artist'].lower()])
                final_other = len([t for t in result if seed_artist_lower not in t['artist'].lower()])
                
                logger.info(f"✅ Forced variety: Now have {final_other} other-artist tracks (replaced {can_replace} same-artist)")
    
    logger.info(f"✅ Returning {len(result)} recommendations (interleaved: {len(interleaved)}, scored: {len(scored_tracks)}, limit: {limit})")
    if len(result) > 0:
        same_count = len([t for t in result if seed_artist_lower in t['artist'].lower()])
        other_count = len([t for t in result if seed_artist_lower not in t['artist'].lower()])
        variety_pct = (other_count / len(result) * 100) if len(result) > 0 else 0.0
        logger.info(f"   Final mix: {same_count} same-artist, {other_count} other-artist ({variety_pct:.1f}% variety)")
    else:
        logger.warning("   No recommendations to return!")
    
    if len(result) < 3:
        logger.warning(f"⚠️ Only returning {len(result)} recommendations! This may indicate filtering is too aggressive or not enough candidates were found.")
        logger.warning(f"   Candidates collected: {len(candidates)}, Unique after filter: {len(unique_candidates)}, Scored: {len(scored_tracks)}")
    
    return result


def enrich_track_features(track: Dict, seed_features: Optional[Dict] = None) -> Dict:
    """
    Enrich a track with full audio features (call this in background)
    Recalculates similarity score with audio data
    """
    try:
        # Get audio features (this is the slow part - 5-10 seconds)
        features = spotify_client.get_audio_features(track['id'])
        
        if features:
            track['audio_features'] = features
            track['_needs_enrichment'] = False
            
            # If we have seed features, recalculate full score
            if seed_features:
                # Now calculate full score with audio features (45%)
                from recommendation_engine import (
                    normalize_audio_features,
                    apply_feature_weights,
                    cosine_similarity,
                    euclidean_similarity,
                    manhattan_similarity
                )
                
                track_vec = apply_feature_weights(normalize_audio_features(features))
                seed_vec = apply_feature_weights(normalize_audio_features(seed_features))
                
                # Audio similarities
                cos_sim = cosine_similarity(track_vec, seed_vec)
                euc_sim = euclidean_similarity(track_vec, seed_vec)
                man_sim = manhattan_similarity(track_vec, seed_vec)
                feature_score = 0.27 * cos_sim + 0.11 * euc_sim + 0.07 * man_sim
                
                # Combine with existing scores
                metadata = track['metadata']
                
                # Genre/tag score (already calculated)
                seed_tags = []  # Would need to pass this in
                track_tags = metadata.get('genres', []) + metadata.get('lastfm_tags', [])
                jaccard_sim = jaccard_similarity(seed_tags, track_tags) if seed_tags else 0.2
                
                # Full score with audio
                full_score = (
                    0.45 * feature_score +
                    0.30 * metadata['lastfm_similarity'] +
                    0.20 * jaccard_sim +
                    0.025 * calculate_temporal_similarity(2020, metadata['release_year']) +
                    0.025 * calculate_popularity_adjustment(metadata['popularity'])
                )
                
                track['similarity_score'] = full_score
        
        return track
        
    except Exception as e:
        logger.error(f"Error enriching track {track['id']}: {e}")
        track['_needs_enrichment'] = False
        return track


def enrich_batch_async(tracks: List[Dict], batch_size: int = 10, seed_features: Optional[Dict] = None):
    """
    Enrich a batch of tracks in parallel
    Call this in background while user swipes
    """
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for track in tracks[:batch_size]:
            if track.get('_needs_enrichment'):
                future = executor.submit(enrich_track_features, track, seed_features)
                futures.append(future)
        
        # Wait for all to complete
        for future in futures:
            try:
                future.result(timeout=15)  # 15 second timeout per track
            except Exception as e:
                logger.warning(f"Track enrichment failed: {e}")

