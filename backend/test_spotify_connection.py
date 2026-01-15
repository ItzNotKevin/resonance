#!/usr/bin/env python3
"""
Test Spotify API connection and credentials
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("  SPOTIFY API CONNECTION TEST")
print("=" * 70)

# Check if .env file exists
if not os.path.exists('.env'):
    print("\n❌ ERROR: .env file not found!")
    print("\nCreate a file named '.env' in the backend/ directory with:")
    print("SPOTIFY_CLIENT_ID=your_client_id")
    print("SPOTIFY_CLIENT_SECRET=your_client_secret")
    exit(1)

# Check credentials
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

print("\n1. Checking credentials from .env file...")
print(f"   SPOTIFY_CLIENT_ID: {'✅ Found' if client_id else '❌ Missing'}")
if client_id:
    print(f"   Value: {client_id[:10]}...{client_id[-5:] if len(client_id) > 15 else ''}")

print(f"   SPOTIFY_CLIENT_SECRET: {'✅ Found' if client_secret else '❌ Missing'}")
if client_secret:
    print(f"   Value: {client_secret[:10]}...{client_secret[-5:] if len(client_secret) > 15 else ''}")

if not client_id or not client_secret:
    print("\n❌ ERROR: Credentials not found in .env file!")
    print("\nMake sure your .env file looks like this:")
    print("SPOTIFY_CLIENT_ID=abc123...")
    print("SPOTIFY_CLIENT_SECRET=xyz789...")
    print("\n(No quotes, no spaces around =)")
    exit(1)

# Try to connect with spotipy
print("\n2. Testing Spotify API connection...")

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    
    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    print("   ✅ Authentication successful!")
    
    # Test a simple search
    print("\n3. Testing API access with a search...")
    results = sp.search(q='test', type='track', limit=1)
    
    if results and results['tracks']['items']:
        track = results['tracks']['items'][0]
        print(f"   ✅ Search works! Found: {track['name']} by {track['artists'][0]['name']}")
        
        # Test audio features
        print("\n4. Testing audio features access...")
        track_id = track['id']
        features = sp.audio_features([track_id])
        
        if features and features[0]:
            print(f"   ✅ Audio features work!")
            print(f"   Energy: {features[0]['energy']:.2f}")
            print(f"   Danceability: {features[0]['danceability']:.2f}")
            print(f"   Tempo: {features[0]['tempo']:.1f} BPM")
            
            print("\n" + "=" * 70)
            print("  🎉 ALL TESTS PASSED! Your Spotify credentials are working!")
            print("=" * 70)
            print("\nYou can now run: python interactive_test.py")
        else:
            print("   ⚠️  Audio features returned empty")
            print("   This might be a temporary Spotify API issue")
    else:
        print("   ⚠️  Search returned no results")
        
except ImportError:
    print("   ❌ spotipy not installed!")
    print("   Run: pip install -r requirements.txt")
    exit(1)
    
except spotipy.oauth2.SpotifyOauthError as e:
    print(f"   ❌ Authentication failed!")
    print(f"   Error: {e}")
    print("\n   This usually means:")
    print("   1. Your Client ID or Secret is incorrect")
    print("   2. Copy them again from https://developer.spotify.com/dashboard")
    print("   3. Make sure there are no extra spaces in your .env file")
    exit(1)
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"   Type: {type(e).__name__}")
    
    if "403" in str(e) or "Forbidden" in str(e):
        print("\n   403 Forbidden Error - This means:")
        print("   1. Your credentials are valid BUT...")
        print("   2. Your Spotify app might not be properly configured")
        print("\n   Try this:")
        print("   1. Go to https://developer.spotify.com/dashboard")
        print("   2. Click on your app")
        print("   3. Click 'Settings'")
        print("   4. Make sure 'Redirect URIs' has: http://localhost:8000/callback")
        print("   5. Click 'Save'")
        print("   6. Wait 1-2 minutes for changes to take effect")
        print("   7. Try again")
    exit(1)












