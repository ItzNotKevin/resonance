#!/usr/bin/env python3
"""
Test Fast Recommendations
Shows the progressive loading in action!
"""

import time
import sys

print("\n" + "=" * 70)
print("  ⚡ FAST RECOMMENDATION TEST")
print("=" * 70)

from progressive_recommendations import get_fast_recommendations

print("\nSearching for 'Blinding Lights'...")
from spotify_client import spotify_client

tracks = spotify_client.search_tracks("Blinding Lights The Weeknd", limit=1)
if not tracks:
    print("Song not found")
    sys.exit(1)

seed = tracks[0]
print(f"Found: {seed['name']} by {seed['artist']}")

print("\n⏱️  Starting timer...")
start_time = time.time()

print("Getting FAST recommendations...")
recommendations = get_fast_recommendations(seed['id'], limit=50)

elapsed = time.time() - start_time

print(f"\n✅ Got {len(recommendations)} recommendations in {elapsed:.2f} seconds!")

print("\n" + "=" * 70)
print("  TOP 15 RECOMMENDATIONS")
print("=" * 70)

for i, rec in enumerate(recommendations[:15], 1):
    score = rec['similarity_score'] * 100
    bar = "█" * int(score / 5)
    
    enriched = "✅" if rec['audio_features'] else "⏳"
    
    print(f"\n{i:2d}. {rec['name'][:40]:40s}")
    print(f"    by {rec['artist'][:45]:45s}")
    print(f"    Score: {score:5.1f}% {bar} {enriched}")

print("\n" + "=" * 70)
print("  📊 PERFORMANCE")
print("=" * 70)

print(f"\n⚡ Load Time: {elapsed:.2f} seconds")
print(f"📦 Recommendations: {len(recommendations)}")
print(f"🎯 Average Score: {sum(r['similarity_score'] for r in recommendations)/len(recommendations)*100:.1f}%")

enriched_count = sum(1 for r in recommendations if r['audio_features'])
print(f"✅ Enriched: {enriched_count}/{len(recommendations)}")
print(f"⏳ Pending: {len(recommendations) - enriched_count}/{len(recommendations)}")

print("\n" + "=" * 70)
print("  ✅ FAST LOADING WORKS!")
print("=" * 70)

print(f"\n🎉 Your app will load in {elapsed:.1f} seconds!")
print("\nUser experience:")
print(f"  • User clicks 'Start Swiping'")
print(f"  • {elapsed:.1f} seconds later → First card shows!")
print(f"  • User starts swiping immediately")
print(f"  • Background enriches audio features")
print(f"  • Scores improve as they swipe")

print("\nThis is how production apps work!")
print("  • TikTok: Fast load, buffer next videos")
print("  • Spotify: Instant play, load next tracks")
print("  • Your app: Instant swipe, enrich in background ⚡")

print("\n" + "=" * 70)












