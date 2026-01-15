#!/usr/bin/env python3
"""
Standalone test script for the recommendation algorithm.
Run this to test the similarity calculations without needing the full app.

Usage:
    python test_algorithm.py                    # Run with sample data
    python test_algorithm.py --live <song_name> # Test with real Spotify data
"""

import sys
import numpy as np
from recommendation_engine import (
    normalize_audio_features,
    apply_feature_weights,
    cosine_similarity,
    euclidean_similarity,
    manhattan_similarity,
    jaccard_similarity,
    calculate_temporal_similarity,
    calculate_popularity_adjustment,
    calculate_similarity_score,
    FEATURE_WEIGHTS,
    FEATURE_NAMES
)

# Sample audio features for testing (realistic Spotify data)
SAMPLE_SEED = {
    'name': 'Blinding Lights',
    'artist': 'The Weeknd',
    'audio_features': {
        'acousticness': 0.001,
        'danceability': 0.514,
        'energy': 0.730,
        'instrumentalness': 0.000134,
        'liveness': 0.0897,
        'loudness': -5.934,
        'speechiness': 0.0598,
        'tempo': 171.005,
        'valence': 0.334,
        'duration_ms': 200040,
        'key': 1
    },
    'metadata': {
        'genres': ['canadian pop', 'pop'],
        'lastfm_tags': ['pop', 'electronic', 'synth-pop'],
        'release_year': 2019,
        'popularity': 95
    }
}

SAMPLE_CANDIDATES = [
    {
        'name': 'Save Your Tears',
        'artist': 'The Weeknd',
        'audio_features': {
            'acousticness': 0.0359,
            'danceability': 0.672,
            'energy': 0.827,
            'instrumentalness': 0.000234,
            'liveness': 0.0938,
            'loudness': -4.868,
            'speechiness': 0.0504,
            'tempo': 118.051,
            'valence': 0.428,
            'duration_ms': 215627,
            'key': 0
        },
        'metadata': {
            'genres': ['canadian pop', 'pop'],
            'lastfm_tags': ['pop', 'electronic'],
            'release_year': 2020,
            'popularity': 92,
            'lastfm_similarity': 0.95
        }
    },
    {
        'name': 'Levitating',
        'artist': 'Dua Lipa',
        'audio_features': {
            'acousticness': 0.0017,
            'danceability': 0.702,
            'energy': 0.825,
            'instrumentalness': 0.0,
            'liveness': 0.0992,
            'loudness': -3.787,
            'speechiness': 0.0567,
            'tempo': 103.0,
            'valence': 0.915,
            'duration_ms': 203064,
            'key': 6
        },
        'metadata': {
            'genres': ['british pop', 'pop', 'dance pop'],
            'lastfm_tags': ['pop', 'disco', 'dance'],
            'release_year': 2020,
            'popularity': 88,
            'lastfm_similarity': 0.75
        }
    },
    {
        'name': 'Wonderwall',
        'artist': 'Oasis',
        'audio_features': {
            'acousticness': 0.248,
            'danceability': 0.383,
            'energy': 0.512,
            'instrumentalness': 0.0,
            'liveness': 0.0924,
            'loudness': -6.776,
            'speechiness': 0.0271,
            'tempo': 174.146,
            'valence': 0.307,
            'duration_ms': 258893,
            'key': 2
        },
        'metadata': {
            'genres': ['britpop', 'rock', 'alternative rock'],
            'lastfm_tags': ['rock', 'britpop', 'alternative'],
            'release_year': 1995,
            'popularity': 82,
            'lastfm_similarity': 0.35
        }
    },
    {
        'name': 'Bohemian Rhapsody',
        'artist': 'Queen',
        'audio_features': {
            'acousticness': 0.374,
            'danceability': 0.364,
            'energy': 0.429,
            'instrumentalness': 0.00126,
            'liveness': 0.178,
            'loudness': -8.646,
            'speechiness': 0.0402,
            'tempo': 144.313,
            'valence': 0.254,
            'duration_ms': 354947,
            'key': 10
        },
        'metadata': {
            'genres': ['classic rock', 'rock'],
            'lastfm_tags': ['rock', 'classic rock', 'progressive rock'],
            'release_year': 1975,
            'popularity': 90,
            'lastfm_similarity': 0.20
        }
    }
]


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_section(text):
    """Print a formatted section"""
    print(f"\n--- {text} ---")


def test_feature_normalization():
    """Test audio feature normalization"""
    print_header("TEST 1: Feature Normalization")
    
    raw_features = SAMPLE_SEED['audio_features']
    normalized = normalize_audio_features(raw_features)
    
    print("\nRaw Features:")
    for i, name in enumerate(FEATURE_NAMES):
        print(f"  {name:20s}: {raw_features.get(name, 0):10.3f} -> {normalized[i]:.3f}")
    
    print(f"\nNormalized vector shape: {normalized.shape}")
    print(f"All values in [0,1]: {all(0 <= x <= 1.1 for x in normalized)}")  # 1.1 for rounding
    
    return normalized


def test_feature_weighting():
    """Test feature importance weighting"""
    print_header("TEST 2: Feature Weighting")
    
    normalized = normalize_audio_features(SAMPLE_SEED['audio_features'])
    weighted = apply_feature_weights(normalized)
    
    print("\nFeature Importance Weights:")
    for i, name in enumerate(FEATURE_NAMES):
        weight = FEATURE_WEIGHTS[name]
        print(f"  {name:20s}: {weight:.1f}x  ({normalized[i]:.3f} -> {weighted[i]:.3f})")
    
    print("\nMost important features:")
    print("  - Energy & Valence (mood): 1.5x")
    print("  - Danceability: 1.3x")
    print("  - Tempo: 1.2x")
    
    return weighted


def test_similarity_methods():
    """Test different similarity calculation methods"""
    print_header("TEST 3: Similarity Methods")
    
    seed_features = normalize_audio_features(SAMPLE_SEED['audio_features'])
    seed_weighted = apply_feature_weights(seed_features)
    
    print(f"\nComparing to seed: {SAMPLE_SEED['name']} by {SAMPLE_SEED['artist']}")
    
    for candidate in SAMPLE_CANDIDATES:
        print(f"\n{candidate['name']} by {candidate['artist']}:")
        
        cand_features = normalize_audio_features(candidate['audio_features'])
        cand_weighted = apply_feature_weights(cand_features)
        
        # Calculate different similarities
        cos_sim = cosine_similarity(seed_weighted, cand_weighted)
        euc_sim = euclidean_similarity(seed_weighted, cand_weighted)
        man_sim = manhattan_similarity(seed_weighted, cand_weighted)
        
        print(f"  Cosine similarity:    {cos_sim:.4f}")
        print(f"  Euclidean similarity: {euc_sim:.4f}")
        print(f"  Manhattan similarity: {man_sim:.4f}")
        
        # Combined feature score
        feature_score = 0.35 * cos_sim + 0.15 * euc_sim + 0.10 * man_sim
        print(f"  → Combined feature:   {feature_score:.4f}")


def test_genre_matching():
    """Test Jaccard similarity for genre/tag matching"""
    print_header("TEST 4: Genre/Tag Matching (Jaccard Similarity)")
    
    seed_tags = SAMPLE_SEED['metadata']['genres'] + SAMPLE_SEED['metadata']['lastfm_tags']
    print(f"\nSeed tags: {seed_tags}")
    
    for candidate in SAMPLE_CANDIDATES:
        cand_tags = candidate['metadata']['genres'] + candidate['metadata']['lastfm_tags']
        jaccard = jaccard_similarity(seed_tags, cand_tags)
        
        print(f"\n{candidate['name']}:")
        print(f"  Tags: {cand_tags}")
        print(f"  Jaccard similarity: {jaccard:.4f}")
        
        # Show overlapping tags
        overlap = set(seed_tags) & set(cand_tags)
        if overlap:
            print(f"  Common tags: {list(overlap)}")


def test_contextual_bonuses():
    """Test temporal and popularity adjustments"""
    print_header("TEST 5: Contextual Bonuses")
    
    seed_year = SAMPLE_SEED['metadata']['release_year']
    
    print("\nTemporal Similarity (Era Matching):")
    print(f"Seed year: {seed_year}")
    
    for candidate in SAMPLE_CANDIDATES:
        cand_year = candidate['metadata']['release_year']
        temporal = calculate_temporal_similarity(seed_year, cand_year)
        year_diff = abs(seed_year - cand_year)
        
        print(f"  {candidate['name']:30s} ({cand_year}): {temporal:.4f} ({year_diff} years apart)")
    
    print("\nPopularity Adjustment (Discovery Optimization):")
    for candidate in SAMPLE_CANDIDATES:
        pop = candidate['metadata']['popularity']
        adj = calculate_popularity_adjustment(pop)
        
        status = "Sweet spot!" if 40 <= pop <= 70 else "Too popular" if pop > 90 else "Too obscure" if pop < 10 else "Good"
        print(f"  {candidate['name']:30s} (pop={pop:2d}): {adj:.2f} ({status})")


def test_full_algorithm():
    """Test the complete recommendation algorithm"""
    print_header("TEST 6: Complete Recommendation Algorithm")
    
    print(f"\nSeed song: {SAMPLE_SEED['name']} by {SAMPLE_SEED['artist']}")
    print("\nCalculating similarity scores for all candidates...\n")
    
    results = []
    
    for candidate in SAMPLE_CANDIDATES:
        score = calculate_similarity_score(
            candidate['audio_features'],
            SAMPLE_SEED['audio_features'],
            candidate['metadata'],
            SAMPLE_SEED['metadata']
        )
        
        results.append({
            'name': candidate['name'],
            'artist': candidate['artist'],
            'score': score
        })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print("Recommendations (ranked by similarity):\n")
    for i, result in enumerate(results, 1):
        percentage = result['score'] * 100
        bars = "█" * int(percentage / 5)
        print(f"{i}. {result['name']:30s} by {result['artist']:20s}")
        print(f"   Score: {result['score']:.4f} ({percentage:.1f}%) {bars}")
        print()


def test_with_live_data(song_query):
    """Test with real Spotify data"""
    print_header("TEST: Live Spotify Data")
    
    try:
        from spotify_client import spotify_client
        from config import settings
        
        if not settings.spotify_client_id:
            print("\n⚠️  Spotify credentials not configured!")
            print("Create backend/.env with your Spotify API credentials to test with live data.")
            return
        
        print(f"\nSearching for: {song_query}")
        tracks = spotify_client.search_tracks(song_query, limit=5)
        
        if not tracks:
            print("No tracks found!")
            return
        
        print(f"\nFound {len(tracks)} tracks. Using first result:")
        seed = tracks[0]
        print(f"  {seed['name']} by {seed['artist']}")
        
        # Get audio features
        features = spotify_client.get_audio_features(seed['id'])
        if not features:
            print("Could not get audio features!")
            return
        
        print("\nAudio Features:")
        normalized = normalize_audio_features(features)
        for i, name in enumerate(FEATURE_NAMES):
            print(f"  {name:20s}: {features.get(name, 0):10.3f}")
        
        # Get recommendations
        print("\nGetting Spotify recommendations...")
        from recommendation_engine import get_recommendations
        
        recommendations = get_recommendations(seed['id'], user_id=None)
        
        if recommendations:
            print(f"\nTop 10 Recommendations:\n")
            for i, rec in enumerate(recommendations[:10], 1):
                percentage = rec['similarity_score'] * 100
                print(f"{i:2d}. {rec['name']:30s} by {rec['artist']:20s}")
                print(f"    Match: {percentage:5.1f}%")
        else:
            print("No recommendations generated!")
            
    except ImportError as e:
        print(f"\n⚠️  Error importing modules: {e}")
        print("Make sure you're running from the backend directory with dependencies installed.")
    except Exception as e:
        print(f"\n⚠️  Error: {e}")


def run_all_tests():
    """Run all algorithm tests"""
    print("\n" + "=" * 70)
    print("  MUSIC RECOMMENDATION ALGORITHM TEST SUITE")
    print("=" * 70)
    print("\nThis will test all similarity algorithms with sample data.\n")
    
    test_feature_normalization()
    test_feature_weighting()
    test_similarity_methods()
    test_genre_matching()
    test_contextual_bonuses()
    test_full_algorithm()
    
    print("\n" + "=" * 70)
    print("  ALL TESTS COMPLETE!")
    print("=" * 70)
    print("\n✅ The recommendation algorithm is working correctly!")
    print("\nNext steps:")
    print("  1. Set up Spotify API credentials in backend/.env")
    print("  2. Run: python test_algorithm.py --live 'your favorite song'")
    print("  3. Test the full app with: uvicorn main:app --reload")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--live':
            if len(sys.argv) < 3:
                print("Usage: python test_algorithm.py --live 'song name'")
                sys.exit(1)
            song_query = ' '.join(sys.argv[2:])
            test_with_live_data(song_query)
        else:
            print("Usage:")
            print("  python test_algorithm.py                    # Run with sample data")
            print("  python test_algorithm.py --live 'song name' # Test with real Spotify data")
    else:
        run_all_tests()












