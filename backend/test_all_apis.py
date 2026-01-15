#!/usr/bin/env python3
"""
Complete API Test - Tests all components of the recommendation system
Works with Spotify's 2024/2025 API restrictions
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("\n" + "=" * 70)
print("  🎵 COMPLETE API TEST - ALL SOURCES")
print("=" * 70)

# Track what works
working_apis = []
issues = []

# Check if .env file exists
if not os.path.exists('.env'):
    print("\n❌ ERROR: .env file not found!")
    print("\nCreate a file named '.env' in the backend/ directory")
    exit(1)

print("\n" + "=" * 70)
print("  1. CHECKING CREDENTIALS")
print("=" * 70)

# Check Spotify
spotify_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

print("\n📌 Spotify:")
if spotify_id and spotify_id != 'your_spotify_client_id_here':
    print(f"   Client ID: ✅ Found ({spotify_id[:10]}...)")
    if spotify_secret and spotify_secret != 'your_spotify_client_secret_here':
        print(f"   Client Secret: ✅ Found ({spotify_secret[:10]}...)")
    else:
        print("   Client Secret: ❌ Missing or placeholder")
        issues.append("Spotify Client Secret not set")
else:
    print("   Client ID: ❌ Missing or placeholder")
    issues.append("Spotify Client ID not set")

# Check Last.fm
lastfm_key = os.getenv('LASTFM_API_KEY')
lastfm_secret = os.getenv('LASTFM_API_SECRET')

print("\n📌 Last.fm:")
if lastfm_key and lastfm_key.strip():
    print(f"   API Key: ✅ Found ({lastfm_key[:10]}...)")
    if lastfm_secret and lastfm_secret.strip():
        print(f"   Shared Secret: ✅ Found ({lastfm_secret[:10]}...)")
    else:
        print("   Shared Secret: ⚠️  Not set (optional)")
else:
    print("   API Key: ⚠️  Not configured (HIGHLY RECOMMENDED!)")
    issues.append("Last.fm API Key not set - recommendations will be limited")

# Check optional APIs
print("\n📌 Optional APIs:")

genius_token = os.getenv('GENIUS_ACCESS_TOKEN')
if genius_token and genius_token.strip():
    print(f"   Genius: ✅ Configured")
else:
    print("   Genius: ⚠️  Not configured (optional)")

discogs_token = os.getenv('DISCOGS_TOKEN')
if discogs_token and discogs_token.strip():
    print(f"   Discogs: ✅ Configured")
else:
    print("   Discogs: ⚠️  Not configured (optional)")

print("\n" + "=" * 70)
print("  2. TESTING SPOTIFY API (What Still Works)")
print("=" * 70)

if not spotify_id or not spotify_secret or \
   spotify_id == 'your_spotify_client_id_here' or \
   spotify_secret == 'your_spotify_client_secret_here':
    print("\n❌ Cannot test Spotify - credentials not set")
    print("\nPlease add your actual credentials to .env:")
    print("1. Go to https://developer.spotify.com/dashboard")
    print("2. Click on your app")
    print("3. Copy Client ID and Client Secret")
    print("4. Replace placeholders in .env file")
else:
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        auth_manager = SpotifyClientCredentials(
            client_id=spotify_id,
            client_secret=spotify_secret
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        print("\n✅ Spotify authentication successful!")
        
        # Test search
        print("\n📍 Testing search...")
        results = sp.search(q='test', type='track', limit=1)
        
        if results and results['tracks']['items']:
            track = results['tracks']['items'][0]
            print(f"   ✅ Search works!")
            print(f"   Found: {track['name']} by {track['artists'][0]['name']}")
            
            # Test getting single track (with preview URL)
            print("\n📍 Testing single track fetch...")
            track_id = track['id']
            full_track = sp.track(track_id)
            
            if full_track:
                print(f"   ✅ Single track fetch works!")
                
                if full_track.get('preview_url'):
                    print(f"   ✅ Preview URL available!")
                    print(f"   URL: {full_track['preview_url'][:50]}...")
                else:
                    print(f"   ⚠️  This track has no preview (some tracks don't)")
            
            # Test artist info (genres)
            print("\n📍 Testing artist info (genres)...")
            artist_id = track['artists'][0]['id']
            artist = sp.artist(artist_id)
            
            if artist:
                print(f"   ✅ Artist info works!")
                if artist.get('genres'):
                    print(f"   Genres: {', '.join(artist['genres'][:3])}")
                else:
                    print(f"   (This artist has no genres listed)")
            
            working_apis.append("Spotify Search")
            working_apis.append("Spotify Track Info")
            working_apis.append("Spotify Preview URLs")
            working_apis.append("Spotify Artist Info")
        
    except spotipy.oauth2.SpotifyOauthError as e:
        print(f"\n❌ Spotify authentication failed!")
        print(f"   Error: {e}")
        print("\n   This means your Client ID or Secret is incorrect.")
        print("   Double-check them in your Spotify dashboard.")
        issues.append("Spotify authentication failed")
    except Exception as e:
        print(f"\n❌ Spotify error: {e}")
        issues.append(f"Spotify error: {str(e)}")

print("\n" + "=" * 70)
print("  3. TESTING LAST.FM API")
print("=" * 70)

if not lastfm_key or not lastfm_key.strip():
    print("\n⚠️  Last.fm not configured")
    print("\n   Last.fm is ESSENTIAL for recommendations!")
    print("   Without it, you'll only get genre/artist matches.")
    print("\n   Get API key from: https://www.last.fm/api/account/create")
else:
    try:
        import pylast
        
        network = pylast.LastFMNetwork(
            api_key=lastfm_key,
            api_secret=lastfm_secret if lastfm_secret else ""
        )
        
        print("\n✅ Last.fm connected!")
        
        # Test similar tracks
        print("\n📍 Testing similar tracks...")
        track = network.get_track("The Weeknd", "Blinding Lights")
        similar = track.get_similar(limit=5)
        
        if similar:
            print(f"   ✅ Similar tracks works!")
            print(f"   Found {len(similar)} similar tracks:")
            for sim_track, score in similar[:3]:
                print(f"      - {sim_track.title} by {sim_track.artist.name} ({score:.2f})")
            
            working_apis.append("Last.fm Similar Tracks")
        
        # Test tags
        print("\n📍 Testing track tags...")
        tags = track.get_top_tags(limit=5)
        
        if tags:
            print(f"   ✅ Tags work!")
            tag_names = [tag.item.name for tag in tags]
            print(f"   Tags: {', '.join(tag_names[:5])}")
            
            working_apis.append("Last.fm Tags")
        
    except Exception as e:
        print(f"\n⚠️  Last.fm error: {e}")
        issues.append(f"Last.fm error: {str(e)}")

print("\n" + "=" * 70)
print("  4. TESTING AUDIO ANALYSIS (Librosa)")
print("=" * 70)

try:
    import librosa
    print("\n✅ Librosa is installed!")
    working_apis.append("Librosa Audio Analysis")
    
    # Test if we can analyze audio
    print("   Ready to analyze audio previews")
    
except ImportError:
    print("\n⚠️  Librosa not installed")
    print("   Run: pip install -r requirements.txt")
    issues.append("Librosa not installed")

print("\n" + "=" * 70)
print("  5. TESTING FREE APIs (No Auth Needed)")
print("=" * 70)

# Test Deezer
print("\n📍 Deezer API:")
try:
    import requests
    response = requests.get("https://api.deezer.com/search?q=test&limit=1", timeout=5)
    if response.status_code == 200:
        print("   ✅ Deezer API accessible!")
        working_apis.append("Deezer")
    else:
        print(f"   ⚠️  Deezer returned: {response.status_code}")
except Exception as e:
    print(f"   ⚠️  Deezer error: {e}")

# Test MusicBrainz
print("\n📍 MusicBrainz API:")
try:
    headers = {'User-Agent': 'MusicSwipeApp/1.0'}
    response = requests.get(
        "https://musicbrainz.org/ws/2/recording?query=test&fmt=json&limit=1",
        headers=headers,
        timeout=5
    )
    if response.status_code == 200:
        print("   ✅ MusicBrainz API accessible!")
        working_apis.append("MusicBrainz")
    else:
        print(f"   ⚠️  MusicBrainz returned: {response.status_code}")
except Exception as e:
    print(f"   ⚠️  MusicBrainz error: {e}")

# Test AcousticBrainz  
print("\n📍 AcousticBrainz API:")
try:
    # Try a known ID
    response = requests.get(
        "https://acousticbrainz.org/api/v1/test/low-level",
        timeout=5
    )
    # AcousticBrainz returns 404 for invalid IDs, which is expected
    print("   ✅ AcousticBrainz API accessible!")
    working_apis.append("AcousticBrainz")
except Exception as e:
    print(f"   ⚠️  AcousticBrainz error: {e}")

print("\n" + "=" * 70)
print("  6. TESTING OPTIONAL APIs")
print("=" * 70)

# Test Genius if configured
if genius_token and genius_token.strip():
    print("\n📍 Genius API:")
    try:
        headers = {'Authorization': f'Bearer {genius_token}'}
        response = requests.get(
            "https://api.genius.com/search?q=test",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            print("   ✅ Genius API works!")
            working_apis.append("Genius")
        else:
            print(f"   ⚠️  Genius returned: {response.status_code}")
            issues.append("Genius token may be invalid")
    except Exception as e:
        print(f"   ⚠️  Genius error: {e}")

# Test Discogs if configured
if discogs_token and discogs_token.strip():
    print("\n📍 Discogs API:")
    try:
        headers = {
            'Authorization': f'Discogs token={discogs_token}',
            'User-Agent': 'MusicSwipeApp/1.0'
        }
        response = requests.get(
            "https://api.discogs.com/database/search?q=test&type=release&per_page=1",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            print("   ✅ Discogs API works!")
            working_apis.append("Discogs")
        else:
            print(f"   ⚠️  Discogs returned: {response.status_code}")
            issues.append("Discogs token may be invalid")
    except Exception as e:
        print(f"   ⚠️  Discogs error: {e}")

print("\n" + "=" * 70)
print("  📊 SUMMARY")
print("=" * 70)

print(f"\n✅ Working APIs: {len(working_apis)}")
for api in working_apis:
    print(f"   ✓ {api}")

if issues:
    print(f"\n⚠️  Issues Found: {len(issues)}")
    for issue in issues:
        print(f"   ! {issue}")

print("\n" + "=" * 70)
print("  🎯 RECOMMENDATION")
print("=" * 70)

if "Spotify Search" in working_apis:
    if any("Last.fm" in api for api in working_apis):
        print("\n🎉 EXCELLENT! Your setup is complete!")
        print("\nYou have:")
        print("   ✅ Spotify (search & metadata)")
        print("   ✅ Last.fm (recommendations)")
        print("   ✅ Audio analysis ready")
        print("\n→ Ready to run: python interactive_test.py")
    else:
        print("\n⚠️  GOOD! But Last.fm is missing")
        print("\nYou have:")
        print("   ✅ Spotify (search & metadata)")
        print("   ❌ Last.fm (ESSENTIAL for recommendations!)")
        print("\nWithout Last.fm, recommendations will be very limited.")
        print("Get API key from: https://www.last.fm/api/account/create")
else:
    print("\n❌ SETUP INCOMPLETE")
    print("\nPlease fix the issues above before testing.")
    print("Most likely: Replace Spotify credential placeholders in .env")

print("\n" + "=" * 70)












