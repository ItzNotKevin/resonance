#!/usr/bin/env python3
"""
Test if we can get track information without audio-features endpoint
This is a workaround if audio-features returns 403
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)

sp = spotipy.Spotify(auth_manager=auth_manager)

print("Testing alternative approach...")
print("\n1. Searching for a song...")

results = sp.search(q='blinding lights', type='track', limit=1)
track = results['tracks']['items'][0]

print(f"   Found: {track['name']} by {track['artists'][0]['name']}")

print("\n2. Getting track details...")
track_id = track['id']
track_details = sp.track(track_id)

print(f"   ✅ Track details work!")
print(f"   Popularity: {track_details['popularity']}")
print(f"   Duration: {track_details['duration_ms']}ms")
print(f"   Album: {track_details['album']['name']}")

print("\n3. Trying audio analysis (alternative to audio features)...")
try:
    analysis = sp.audio_analysis(track_id)
    print(f"   ✅ Audio analysis works!")
    print(f"   Tempo: {analysis['track']['tempo']:.1f} BPM")
    print(f"   Loudness: {analysis['track']['loudness']:.1f} dB")
    print(f"   Duration: {analysis['track']['duration']:.1f}s")
except Exception as e:
    print(f"   ❌ Audio analysis also blocked: {e}")

print("\n4. Trying to get multiple tracks' audio features at once...")
try:
    features = sp.audio_features([track_id])
    if features and features[0]:
        print(f"   ✅ Audio features work now!")
        print(f"   Energy: {features[0]['energy']:.2f}")
        print(f"   Danceability: {features[0]['danceability']:.2f}")
    else:
        print(f"   ⚠️  Audio features returned empty")
except Exception as e:
    print(f"   ❌ Still blocked: {e}")

print("\n" + "="*70)
print("If audio-features is still blocked, we can:")
print("1. Wait for Spotify to activate your app (can take up to 24 hours)")
print("2. Use audio-analysis as a fallback (has similar data)")
print("3. Contact Spotify support to enable audio-features access")
print("="*70)












