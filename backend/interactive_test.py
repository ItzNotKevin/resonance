#!/usr/bin/env python3
"""
Interactive Recommendation Tester
Test the recommendation algorithm with your own song choices!

This script lets you:
1. Search for any song on Spotify
2. See its audio features
3. Get real recommendations
4. View similarity scores and breakdowns
"""

import sys
from recommendation_engine import get_recommendations, calculate_similarity_score
from spotify_client import spotify_client
from config import settings


def print_banner():
    """Print welcome banner"""
    print("\n" + "=" * 70)
    print("  🎵 MUSIC RECOMMENDATION ALGORITHM TESTER 🎵")
    print("=" * 70)
    print("\nTest your music recommendations with real Spotify data!")
    print()


def check_credentials():
    """Check if Spotify credentials are configured"""
    if not settings.spotify_client_id or not settings.spotify_client_secret:
        print("⚠️  Spotify API credentials not found!")
        print("\nTo use this tester, you need to:")
        print("1. Go to https://developer.spotify.com/dashboard")
        print("2. Create an app and get your Client ID and Secret")
        print("3. Create a file: backend/.env")
        print("4. Add these lines:")
        print("   SPOTIFY_CLIENT_ID=your_client_id_here")
        print("   SPOTIFY_CLIENT_SECRET=your_client_secret_here")
        print("\nSee SETUP_GUIDE.md for detailed instructions.")
        return False
    
    # Test connection
    if not spotify_client.client:
        print("⚠️  Could not connect to Spotify API!")
        print("Check your credentials in backend/.env")
        return False
    
    return True


def search_song():
    """Search for a song"""
    while True:
        query = input("\n🔍 Search for a song (or 'q' to quit): ").strip()
        
        if query.lower() in ['q', 'quit', 'exit']:
            return None
        
        if len(query) < 2:
            print("Please enter at least 2 characters")
            continue
        
        print(f"\nSearching for: {query}...")
        tracks = spotify_client.search_tracks(query, limit=10)
        
        if not tracks:
            print("No results found. Try a different search.")
            continue
        
        print(f"\nFound {len(tracks)} results:\n")
        for i, track in enumerate(tracks, 1):
            print(f"{i:2d}. {track['name']:40s} by {track['artist']:30s} [{track['popularity']:2d}]")
        
        while True:
            choice = input("\nSelect a song (1-10) or 's' to search again: ").strip()
            
            if choice.lower() == 's':
                break
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(tracks):
                    return tracks[idx]
                else:
                    print(f"Please enter a number between 1 and {len(tracks)}")
            except ValueError:
                print("Please enter a valid number or 's'")
    
    return None


def show_audio_features(track):
    """Display audio features for a track"""
    print("\n" + "-" * 70)
    print(f"  📊 Audio Features: {track['name']}")
    print("-" * 70)
    
    features = spotify_client.get_audio_features(track['id'])
    if not features:
        print("Could not get audio features")
        return None
    
    # Display in a nice format
    print("\n🎼 Musical Characteristics:")
    print(f"  Energy:          {'█' * int(features['energy'] * 20):20s} {features['energy']:.2f}")
    print(f"  Danceability:    {'█' * int(features['danceability'] * 20):20s} {features['danceability']:.2f}")
    print(f"  Valence (mood):  {'█' * int(features['valence'] * 20):20s} {features['valence']:.2f}")
    print(f"  Acousticness:    {'█' * int(features['acousticness'] * 20):20s} {features['acousticness']:.2f}")
    print(f"  Instrumentals:   {'█' * int(features['instrumentalness'] * 20):20s} {features['instrumentalness']:.2f}")
    
    print("\n🎚️  Audio Properties:")
    print(f"  Tempo:           {features['tempo']:.1f} BPM")
    print(f"  Loudness:        {features['loudness']:.1f} dB")
    print(f"  Duration:        {features['duration_ms'] // 1000} seconds")
    print(f"  Key:             {features['key']} (0=C, 1=C#, 2=D, etc.)")
    
    return features


def get_and_display_recommendations(track, features):
    """Get recommendations and display with scores"""
    print("\n" + "=" * 70)
    print("  🎯 GENERATING RECOMMENDATIONS...")
    print("=" * 70)
    
    print("\nAnalyzing song characteristics...")
    print("Searching for similar tracks...")
    print("Calculating similarity scores...\n")
    
    try:
        recommendations = get_recommendations(track['id'], user_id=None)
        
        if not recommendations:
            print("❌ No recommendations found. This shouldn't happen!")
            return
        
        print(f"✅ Found {len(recommendations)} recommendations!\n")
        
        # Show top 20
        print("=" * 70)
        print("  TOP 20 RECOMMENDATIONS")
        print("=" * 70)
        
        for i, rec in enumerate(recommendations[:20], 1):
            score = rec['similarity_score']
            percentage = score * 100
            
            # Create visual bar
            bar_length = int(percentage / 5)
            bar = "█" * bar_length
            
            print(f"\n{i:2d}. {rec['name'][:35]:35s} by {rec['artist'][:25]:25s}")
            print(f"    Match: {percentage:5.1f}% {bar}")
            
            # Show why it matched (top contributing factors)
            if i <= 5:  # Show details for top 5
                print(f"    Genres: {', '.join(rec['metadata']['genres'][:3]) if rec['metadata']['genres'] else 'N/A'}")
        
        # Show a detailed breakdown for the top recommendation
        if recommendations:
            show_detailed_breakdown(track, features, recommendations[0])
    
    except Exception as e:
        print(f"❌ Error getting recommendations: {e}")
        import traceback
        traceback.print_exc()


def show_detailed_breakdown(seed_track, seed_features, top_rec):
    """Show detailed similarity breakdown for top recommendation"""
    print("\n" + "=" * 70)
    print("  🔬 DETAILED BREAKDOWN - TOP RECOMMENDATION")
    print("=" * 70)
    
    print(f"\n{top_rec['name']} by {top_rec['artist']}")
    print(f"Overall Match: {top_rec['similarity_score'] * 100:.1f}%\n")
    
    # Get metadata for seed
    seed_genres = []
    for artist_id in seed_track.get('artist_ids', []):
        seed_genres.extend(spotify_client.get_artist_genres(artist_id))
    
    seed_metadata = {
        'genres': seed_genres,
        'lastfm_tags': [],
        'release_year': int(seed_track['release_date'].split('-')[0]) if 'release_date' in seed_track else 2020,
        'popularity': seed_track['popularity']
    }
    
    # Calculate component scores
    from recommendation_engine import (
        normalize_audio_features,
        apply_feature_weights,
        cosine_similarity,
        euclidean_similarity,
        manhattan_similarity,
        jaccard_similarity,
        calculate_temporal_similarity,
        calculate_popularity_adjustment
    )
    
    seed_vec = apply_feature_weights(normalize_audio_features(seed_features))
    rec_vec = apply_feature_weights(normalize_audio_features(top_rec['audio_features']))
    
    cos_sim = cosine_similarity(seed_vec, rec_vec)
    euc_sim = euclidean_similarity(seed_vec, rec_vec)
    man_sim = manhattan_similarity(seed_vec, rec_vec)
    
    feature_score = 0.35 * cos_sim + 0.15 * euc_sim + 0.10 * man_sim
    
    seed_tags = seed_metadata['genres'] + seed_metadata.get('lastfm_tags', [])
    rec_tags = top_rec['metadata']['genres'] + top_rec['metadata']['lastfm_tags']
    jaccard_sim = jaccard_similarity(seed_tags, rec_tags)
    
    temporal = calculate_temporal_similarity(
        seed_metadata['release_year'],
        top_rec['metadata']['release_year']
    )
    
    pop_adj = calculate_popularity_adjustment(top_rec['metadata']['popularity'])
    
    print("Score Components:")
    print(f"  🎵 Audio Features (60%):  {feature_score:.4f}")
    print(f"     - Cosine similarity:    {cos_sim:.4f}")
    print(f"     - Euclidean distance:   {euc_sim:.4f}")
    print(f"     - Manhattan distance:   {man_sim:.4f}")
    print(f"\n  🏷️  Genre/Tags (20%):     {jaccard_sim:.4f}")
    print(f"     - Common tags: {list(set(seed_tags) & set(rec_tags))[:5]}")
    print(f"\n  👥 Last.fm Score (15%):   {top_rec['metadata'].get('lastfm_similarity', 0):.4f}")
    print(f"\n  📅 Era Match (2.5%):      {temporal:.4f}")
    print(f"     - Seed: {seed_metadata['release_year']}, This: {top_rec['metadata']['release_year']}")
    print(f"\n  ⭐ Popularity (2.5%):     {pop_adj:.4f}")
    print(f"     - Popularity: {top_rec['metadata']['popularity']}/100")
    
    # Show feature differences
    print("\n🎼 Feature Comparison:")
    print(f"{'Feature':<20} {'Seed':>10} {'Match':>10} {'Diff':>10}")
    print("-" * 52)
    
    important_features = ['energy', 'valence', 'danceability', 'tempo', 'acousticness']
    for feat in important_features:
        seed_val = seed_features.get(feat, 0)
        rec_val = top_rec['audio_features'].get(feat, 0)
        diff = abs(seed_val - rec_val)
        
        if feat == 'tempo':
            print(f"{feat:<20} {seed_val:>8.1f}  {rec_val:>8.1f}  {diff:>8.1f}")
        else:
            print(f"{feat:<20} {seed_val:>10.3f}  {rec_val:>10.3f}  {diff:>10.3f}")


def main():
    """Main interactive loop"""
    print_banner()
    
    # Check credentials
    if not check_credentials():
        return
    
    print("✅ Connected to Spotify API successfully!\n")
    
    while True:
        # Search for a song
        track = search_song()
        
        if track is None:
            print("\n👋 Thanks for testing! Goodbye.\n")
            break
        
        print(f"\n✅ Selected: {track['name']} by {track['artist']}")
        
        # Show audio features
        features = show_audio_features(track)
        if not features:
            continue
        
        # Ask if they want recommendations
        print("\n" + "=" * 70)
        response = input("Generate recommendations? (Y/n): ").strip().lower()
        
        if response in ['', 'y', 'yes']:
            get_and_display_recommendations(track, features)
        
        # Continue or exit
        print("\n" + "=" * 70)
        cont = input("\nTest another song? (Y/n): ").strip().lower()
        if cont not in ['', 'y', 'yes']:
            print("\n👋 Thanks for testing! Goodbye.\n")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()












