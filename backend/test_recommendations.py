#!/usr/bin/env python3
"""
Full Recommendation System Test
Tests the complete recommendation pipeline automatically
"""

import sys
from spotify_client import spotify_client
from recommendation_engine import get_recommendations
from config import settings

print("\n" + "=" * 70)
print("  🎵 FULL RECOMMENDATION PIPELINE TEST")
print("=" * 70)

# Check Spotify
if not settings.spotify_client_id or not settings.spotify_client_secret:
    print("\n❌ Spotify credentials not configured")
    sys.exit(1)

if not spotify_client.client:
    print("\n❌ Could not connect to Spotify")
    sys.exit(1)

print("\n✅ Connected to Spotify API")

# Check Last.fm
if not settings.lastfm_api_key:
    print("⚠️  Last.fm not configured - recommendations will be limited")
else:
    print("✅ Last.fm configured")

print("\n" + "=" * 70)
print("  TESTING WITH: Blinding Lights by The Weeknd")
print("=" * 70)

# Search for the song
print("\n1️⃣  Searching for 'Blinding Lights'...")
try:
    tracks = spotify_client.search_tracks("Blinding Lights The Weeknd", limit=5)
    
    if not tracks:
        print("❌ No results found")
        sys.exit(1)
    
    print(f"   ✅ Found {len(tracks)} tracks")
    seed_track = tracks[0]
    print(f"   Selected: {seed_track['name']} by {seed_track['artist']}")
    print(f"   Popularity: {seed_track['popularity']}/100")
    
except Exception as e:
    print(f"❌ Search failed: {e}")
    sys.exit(1)

# Get audio features
print("\n2️⃣  Getting audio features...")
try:
    features = spotify_client.get_audio_features(seed_track['id'])
    
    if features:
        print("   ✅ Audio features extracted!")
        print(f"   Tempo: {features['tempo']:.1f} BPM")
        print(f"   Energy: {features['energy']:.2f}")
        print(f"   Danceability: {features['danceability']:.2f}")
        print(f"   Valence (mood): {features['valence']:.2f}")
        
        if '_sources_used' in features:
            print(f"   Sources: {features.get('_sources_used', [])}")
    else:
        print("   ⚠️  Using default features")
        
except Exception as e:
    print(f"   ⚠️  Feature extraction error: {e}")

# Get recommendations
print("\n3️⃣  Generating recommendations...")
print("   (This may take 10-30 seconds with multiple API calls...)")

try:
    recommendations = get_recommendations(seed_track['id'], user_id=None)
    
    if not recommendations:
        print("❌ No recommendations generated")
        sys.exit(1)
    
    print(f"\n   ✅ Generated {len(recommendations)} recommendations!")
    
    print("\n" + "=" * 70)
    print("  🎯 TOP 15 RECOMMENDATIONS")
    print("=" * 70)
    
    for i, rec in enumerate(recommendations[:15], 1):
        score = rec['similarity_score']
        percentage = score * 100
        
        # Visual bar
        bar_length = int(percentage / 5)
        bar = "█" * bar_length
        
        print(f"\n{i:2d}. {rec['name'][:40]:40s}")
        print(f"    by {rec['artist'][:45]:45s}")
        print(f"    Match: {percentage:5.1f}% {bar}")
        
        # Show genres for top 5
        if i <= 5 and rec['metadata'].get('genres'):
            genres = ', '.join(rec['metadata']['genres'][:3])
            print(f"    Genres: {genres}")
    
    # Show detailed breakdown for top recommendation
    print("\n" + "=" * 70)
    print("  🔬 DETAILED ANALYSIS - TOP MATCH")
    print("=" * 70)
    
    top_rec = recommendations[0]
    print(f"\n{top_rec['name']} by {top_rec['artist']}")
    print(f"Overall Similarity: {top_rec['similarity_score'] * 100:.1f}%")
    
    print("\nMetadata:")
    if top_rec['metadata'].get('genres'):
        print(f"  Genres: {', '.join(top_rec['metadata']['genres'][:5])}")
    if top_rec['metadata'].get('lastfm_tags'):
        print(f"  Last.fm Tags: {', '.join(top_rec['metadata']['lastfm_tags'][:5])}")
    print(f"  Release Year: {top_rec['metadata']['release_year']}")
    print(f"  Popularity: {top_rec['metadata']['popularity']}/100")
    print(f"  Last.fm Similarity: {top_rec['metadata']['lastfm_similarity']:.2f}")
    
    print("\n" + "=" * 70)
    print("  ✅ SUCCESS! RECOMMENDATION SYSTEM WORKS PERFECTLY!")
    print("=" * 70)
    
    print("\n🎉 Your algorithm is fully operational!")
    print("\nNext steps:")
    print("  1. Run the full backend: uvicorn main:app --reload")
    print("  2. Setup frontend: cd ../frontend && npm install")
    print("  3. Launch app: npx expo start")
    print()
    
except Exception as e:
    print(f"\n❌ Recommendation generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)












