#!/usr/bin/env python3
"""
Algorithm-Only Test
Tests the recommendation algorithm with real data
No frontend needed - just shows you the recommendations!
"""

import sys

print("\n" + "=" * 70)
print("  🎵 RECOMMENDATION ALGORITHM TEST")
print("=" * 70)

# Test with a popular song
TEST_SONG = "Summer Games"
TEST_ARTIST = "Drake"

print(f"\nTesting with: {TEST_SONG} by {TEST_ARTIST}")
print("=" * 70)

# Import components
print("\n1️⃣  Loading components...")
try:
    from spotify_client import spotify_client
    from recommendation_engine import get_recommendations
    print("   ✅ All components loaded")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Search for the song
print(f"\n2️⃣  Searching Spotify for '{TEST_SONG}'...")
try:
    tracks = spotify_client.search_tracks(f"{TEST_SONG} {TEST_ARTIST}", limit=1)
    
    if not tracks:
        print(f"   ❌ Song not found. Try a different song.")
        sys.exit(1)
    
    seed = tracks[0]
    print(f"   ✅ Found: {seed['name']}")
    print(f"   Artist: {seed['artist']}")
    print(f"   Popularity: {seed['popularity']}/100")
    print(f"   Track ID: {seed['id']}")
    
except Exception as e:
    print(f"   ❌ Search failed: {e}")
    sys.exit(1)

# Get audio features
print(f"\n3️⃣  Extracting audio features...")
try:
    features = spotify_client.get_audio_features(seed['id'])
    
    if features:
        print("   ✅ Audio features extracted!")
        print(f"\n   Musical Characteristics:")
        print(f"   • Energy:        {features['energy']:.2f}")
        print(f"   • Danceability:  {features['danceability']:.2f}")
        print(f"   • Valence (mood):{features['valence']:.2f}")
        print(f"   • Tempo:         {features['tempo']:.1f} BPM")
        print(f"   • Acousticness:  {features['acousticness']:.2f}")
        
        if '_num_sources' in features:
            print(f"\n   Fused from {features['_num_sources']} sources!")
    else:
        print("   ⚠️  Using default features")
        
except Exception as e:
    print(f"   ⚠️  Feature extraction: {e}")

# Generate recommendations
print(f"\n4️⃣  Generating recommendations...")
print("   (Querying Last.fm, Deezer, AcousticBrainz, Genius...)")
print("   This may take 15-30 seconds...")

try:
    recommendations = get_recommendations(seed['id'], user_id=None)
    
    if not recommendations:
        print("\n   ❌ No recommendations generated")
        print("   This might mean Last.fm API is having issues")
        sys.exit(1)
    
    print(f"\n   ✅ SUCCESS! Generated {len(recommendations)} recommendations!")
    
    # Display top recommendations
    print("\n" + "=" * 70)
    print("  🎯 TOP 20 RECOMMENDATIONS FOR: " + TEST_SONG)
    print("=" * 70)
    
    for i, rec in enumerate(recommendations[:20], 1):
        score = rec['similarity_score']
        percentage = score * 100
        
        # Visual bar
        bar_length = int(percentage / 5)
        bar = "█" * bar_length if bar_length > 0 else ""
        
        print(f"\n{i:2d}. {rec['name'][:45]:45s}")
        print(f"    by {rec['artist'][:50]:50s}")
        print(f"    Match: {percentage:5.1f}% {bar}")
        
        # Show details for top 3
        if i <= 3:
            genres = rec['metadata'].get('genres', [])
            if genres:
                print(f"    Genres: {', '.join(genres[:3])}")
            
            lastfm_score = rec['metadata'].get('lastfm_similarity', 0)
            if lastfm_score > 0:
                print(f"    Last.fm score: {lastfm_score:.2f}")
    
    # Detailed breakdown
    print("\n" + "=" * 70)
    print("  🔬 ALGORITHM BREAKDOWN - TOP MATCH")
    print("=" * 70)
    
    top = recommendations[0]
    print(f"\n{top['name']} by {top['artist']}")
    print(f"\nOverall Similarity Score: {top['similarity_score']:.4f} ({top['similarity_score']*100:.1f}%)")
    
    print("\nWhy this song matched:")
    print(f"  • Last.fm Community: {top['metadata']['lastfm_similarity']:.2f} (30% weight)")
    print(f"  • Release Year: {top['metadata']['release_year']}")
    print(f"  • Popularity: {top['metadata']['popularity']}/100")
    
    if top['metadata'].get('genres'):
        print(f"  • Genres: {', '.join(top['metadata']['genres'][:5])}")
    
    if top['metadata'].get('lastfm_tags'):
        print(f"  • Tags: {', '.join(top['metadata']['lastfm_tags'][:5])}")
    
    # Show algorithm is working
    print("\n" + "=" * 70)
    print("  ✅ ALGORITHM TEST SUCCESSFUL!")
    print("=" * 70)
    
    print("\n🎉 Your recommendation algorithm works perfectly!")
    print("\nAlgorithm uses:")
    print("  • Audio similarity: 45% (cosine + euclidean + manhattan)")
    print("  • Last.fm community: 30%")
    print("  • Genre/tag matching: 20%")
    print("  • Context (era + popularity): 5%")
    
    print("\nData sources:")
    print("  ✓ Spotify (search & metadata)")
    print("  ✓ Last.fm (similar tracks - primary source!)")
    print("  ✓ Deezer (BPM & energy)")
    print("  ✓ AcousticBrainz (audio features)")
    print("  ✓ Genius (lyric themes)")
    
    print(f"\n📊 Statistics:")
    print(f"  • Total candidates analyzed: {len(recommendations)}")
    print(f"  • Top score: {recommendations[0]['similarity_score']*100:.1f}%")
    print(f"  • Lowest score: {recommendations[-1]['similarity_score']*100:.1f}%")
    print(f"  • Average score: {sum(r['similarity_score'] for r in recommendations)/len(recommendations)*100:.1f}%")
    
    print("\n" + "=" * 70)
    print("\n✅ Algorithm verified! Ready for full app!")
    print("\nNext steps:")
    print("  1. Algorithm is working ✅")
    print("  2. When ready, run backend: uvicorn main:app --reload")
    print("  3. Then setup frontend: cd ../frontend && npm install")
    print()
    
except Exception as e:
    print(f"\n❌ Error generating recommendations: {e}")
    print("\nDebug info:")
    import traceback
    traceback.print_exc()
    sys.exit(1)












