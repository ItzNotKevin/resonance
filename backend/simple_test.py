#!/usr/bin/env python3
"""
Simplified tester using only Spotify's recommendations endpoint
This works even without audio-features access!
"""

import sys
from spotify_client import spotify_client
from config import settings

def print_banner():
    print("\n" + "=" * 70)
    print("  🎵 SIMPLE SPOTIFY RECOMMENDATIONS TESTER")
    print("=" * 70)
    print("\nThis version uses Spotify's recommendation endpoint")
    print("Works even if audio-features is blocked!\n")

def main():
    print_banner()
    
    # Check connection
    if not settings.spotify_client_id or not settings.spotify_client_secret:
        print("❌ Spotify credentials not found in .env file")
        return
    
    if not spotify_client.client:
        print("❌ Could not connect to Spotify")
        return
    
    print("✅ Connected to Spotify!\n")
    
    while True:
        query = input("🔍 Search for a song (or 'q' to quit): ").strip()
        
        if query.lower() in ['q', 'quit', 'exit']:
            print("\n👋 Goodbye!\n")
            break
        
        if len(query) < 2:
            continue
        
        # Search
        print(f"\nSearching for: {query}...")
        tracks = spotify_client.search_tracks(query, limit=10)
        
        if not tracks:
            print("No results found. Try again.")
            continue
        
        print(f"\nFound {len(tracks)} results:\n")
        for i, track in enumerate(tracks, 1):
            print(f"{i:2d}. {track['name'][:40]:40s} by {track['artist'][:30]:30s}")
        
        choice = input("\nSelect a song (1-10): ").strip()
        
        try:
            idx = int(choice) - 1
            if not (0 <= idx < len(tracks)):
                continue
        except:
            continue
        
        selected = tracks[idx]
        print(f"\n✅ Selected: {selected['name']} by {selected['artist']}")
        
        # Get Spotify's native recommendations
        print("\n🎯 Getting recommendations from Spotify...")
        
        try:
            recommendations = spotify_client.get_recommendations(
                seed_tracks=[selected['id']],
                limit=20
            )
            
            if not recommendations:
                print("❌ No recommendations found")
                continue
            
            print(f"\n✅ Found {len(recommendations)} recommendations!\n")
            print("=" * 70)
            print("  TOP RECOMMENDATIONS (from Spotify's algorithm)")
            print("=" * 70)
            
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i:2d}. {rec['name'][:40]:40s}")
                print(f"    by {rec['artist'][:50]:50s}")
                print(f"    Popularity: {rec['popularity']}/100")
                
                # Get artist genres if available
                if rec.get('artist_ids'):
                    genres = spotify_client.get_artist_genres(rec['artist_ids'][0])
                    if genres:
                        print(f"    Genres: {', '.join(genres[:3])}")
            
            print("\n" + "=" * 70)
            print("Note: This uses Spotify's built-in recommendations.")
            print("Once audio-features is enabled, you'll get custom similarity scores!")
            print("=" * 70)
            
        except Exception as e:
            print(f"❌ Error getting recommendations: {e}")
        
        cont = input("\nTest another song? (Y/n): ").strip().lower()
        if cont not in ['', 'y', 'yes']:
            print("\n👋 Thanks for testing!\n")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")












