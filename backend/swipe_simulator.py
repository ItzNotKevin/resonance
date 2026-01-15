#!/usr/bin/env python3
"""
Interactive Swipe Simulator
Simulates the real app swipe experience in terminal
Tests adaptive learning and progressive batching!
"""

import sys
import time
from typing import List, Dict
from spotify_client import spotify_client
from progressive_recommendations import get_fast_recommendations
from recommendation_engine import update_user_preferences
from database import SessionLocal, SwipeHistory, User, UserPreferences, init_db

# Initialize database
init_db()

print("\n" + "=" * 70)
print("  🎵 SWIPE SIMULATOR - Test Your Algorithm!")
print("=" * 70)
print("\nThis simulates the real app swipe experience:")
print("  • Swipe RIGHT (y) = Like the song")
print("  • Swipe LEFT (n) = Pass on the song")
print("  • Algorithm learns your preferences!")
print("  • Recommendations improve as you swipe!")
print("=" * 70)

# Configuration
INITIAL_BATCH_SIZE = 20  # First batch: Enough to start
NEXT_BATCH_SIZE = 15     # Subsequent batches: Smaller, faster
PREFETCH_THRESHOLD = 10  # Start fetching when user reaches card 10 (HALFWAY through 20)
LEARN_INTERVAL = 10      # Update preferences every 10 swipes

# State for background fetching
next_batch_loading = False
next_batch_ready = []

print(f"\n⚙️  Configuration:")
print(f"  • Initial batch: {INITIAL_BATCH_SIZE} songs")
print(f"  • Next batches: {NEXT_BATCH_SIZE} songs")
print(f"  • Prefetch trigger: At card {PREFETCH_THRESHOLD} (background loading)")
print(f"  • Learn interval: Every {LEARN_INTERVAL} swipes")

# Create or get test user
db = SessionLocal()
test_user = db.query(User).filter(User.username == "test_user").first()
if not test_user:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    test_user = User(username="test_user", password_hash=pwd_context.hash("test123"))
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    print(f"\n✅ Created test user (ID: {test_user.id})")
else:
    print(f"\n✅ Using existing test user (ID: {test_user.id})")
db.close()

# Search for seed song
while True:
    seed_query = input("\n🔍 Enter a song to start (or 'q' to quit): ").strip()
    
    if seed_query.lower() in ['q', 'quit', 'exit']:
        print("\n👋 Goodbye!\n")
        sys.exit(0)
    
    if len(seed_query) < 2:
        continue
    
    print(f"\nSearching for: {seed_query}...")
    tracks = spotify_client.search_tracks(seed_query, limit=5)
    
    if not tracks:
        print("No results found. Try again.")
        continue
    
    print(f"\nFound {len(tracks)} results:\n")
    for i, track in enumerate(tracks, 1):
        print(f"{i}. {track['name'][:40]:40s} by {track['artist'][:30]:30s}")
    
    choice = input("\nSelect a song (1-5): ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(tracks):
            seed_track = tracks[idx]
            break
    except:
        print("Invalid choice")

print(f"\n✅ Selected: {seed_track['name']} by {seed_track['artist']}")

# Get initial batch
print(f"\n⏱️  Loading initial batch of {INITIAL_BATCH_SIZE} recommendations...")
start = time.time()

recommendations = get_fast_recommendations(seed_track['id'], limit=INITIAL_BATCH_SIZE)

elapsed = time.time() - start

if not recommendations:
    print("❌ No recommendations found")
    sys.exit(1)

print(f"✅ Loaded {len(recommendations)} songs in {elapsed:.1f} seconds!")

# Swipe loop
current_index = 0
total_swipes = 0
likes = 0
dislikes = 0
swipe_history = []

print("\n" + "=" * 70)
print("  🎴 START SWIPING!")
print("=" * 70)
print("\nCommands:")
print("  y or → = LIKE (swipe right)")
print("  n or ← = PASS (swipe left)")
print("  s = SKIP (don't record swipe)")
print("  q = QUIT")
print("  stats = Show statistics")
print("=" * 70)

while current_index < len(recommendations):
    rec = recommendations[current_index]
    remaining = len(recommendations) - current_index
    
    print(f"\n{'=' * 70}")
    print(f"  Card {current_index + 1}/{len(recommendations)} (📦 {remaining} remaining)")
    print(f"{'=' * 70}")
    
    print(f"\n🎵 {rec['name']}")
    print(f"👤 by {rec['artist']}")
    print(f"💿 {rec['album']}")
    print(f"⭐ Popularity: {rec['metadata']['popularity']}/100")
    print(f"📊 Match Score: {rec['similarity_score']*100:.1f}%")
    
    if rec['metadata'].get('genres'):
        print(f"🏷️  Genres: {', '.join(rec['metadata']['genres'][:3])}")
    
    if rec['metadata'].get('lastfm_tags'):
        print(f"🎯 Tags: {', '.join(rec['metadata']['lastfm_tags'][:5])}")
    
    print(f"\n💚 Likes: {likes} | ❤️‍🔥 Passes: {dislikes} | 📈 Total: {total_swipes}")
    
    # Get swipe input
    while True:
        swipe = input("\n👉 Swipe (y/n/s/q/stats): ").strip().lower()
        
        if swipe in ['y', 'yes', 'right', '→']:
            direction = 'right'
            likes += 1
            total_swipes += 1
            print("💚 LIKED!")
            break
        elif swipe in ['n', 'no', 'left', '←']:
            direction = 'left'
            dislikes += 1
            total_swipes += 1
            print("❤️‍🔥 PASSED")
            break
        elif swipe in ['s', 'skip']:
            direction = None
            print("⏭️  SKIPPED")
            break
        elif swipe in ['q', 'quit', 'exit']:
            print(f"\n\n📊 Final Stats:")
            print(f"   Total Swipes: {total_swipes}")
            print(f"   Likes: {likes} ({likes/total_swipes*100 if total_swipes > 0 else 0:.1f}%)")
            print(f"   Passes: {dislikes}")
            print("\n👋 Thanks for testing!\n")
            sys.exit(0)
        elif swipe == 'stats':
            print(f"\n📊 Current Statistics:")
            print(f"   Total Swipes: {total_swipes}")
            print(f"   Likes: {likes} ({likes/total_swipes*100 if total_swipes > 0 else 0:.1f}%)")
            print(f"   Passes: {dislikes}")
            print(f"   Cards Remaining: {remaining}")
            continue
        else:
            print("Invalid input. Use y/n/s/q")
            continue
    
    # Record swipe if not skipped
    if direction:
        db = SessionLocal()
        try:
            # Get default audio features for recording
            audio_features = rec['audio_features'] if rec['audio_features'] else {
                'energy': 0.5, 'valence': 0.5, 'danceability': 0.5,
                'tempo': 120, 'acousticness': 0.5
            }
            
            swipe_record = SwipeHistory(
                user_id=test_user.id,
                song_id=rec['id'],
                song_name=rec['name'],
                artist_name=rec['artist'],
                direction=direction,
                audio_features=audio_features,
                track_metadata=rec['metadata']
            )
            db.add(swipe_record)
            db.commit()
            
            swipe_history.append({
                'direction': direction,
                'name': rec['name'],
                'score': rec['similarity_score']
            })
            
        finally:
            db.close()
        
        # Update preferences every LEARN_INTERVAL swipes
        if total_swipes > 0 and total_swipes % LEARN_INTERVAL == 0:
            print(f"\n🧠 LEARNING from your {LEARN_INTERVAL} swipes...")
            update_user_preferences(test_user.id)
            print("   ✅ Preferences updated! Future recommendations will be personalized.")
    
    current_index += 1
    
    # PREFETCH next batch in background (seamless experience!)
    # Trigger when user reaches PREFETCH_THRESHOLD (e.g., card 10)
    # By the time they finish current batch, next is ready!
    if current_index == PREFETCH_THRESHOLD and not next_batch_loading and len(next_batch_ready) == 0:
        print(f"\n📦 Reached card {PREFETCH_THRESHOLD}...")
        print(f"   🔄 Loading next {NEXT_BATCH_SIZE} songs in BACKGROUND...")
        print(f"   (You keep swiping - no waiting!)")
        
        # In a real app, this would be a background thread/task
        # For this simulator, we'll fetch it now but show it's "background"
        next_batch_loading = True
        
        try:
            import threading
            
            def fetch_in_background():
                global next_batch_ready, next_batch_loading
                try:
                    new_recs = get_fast_recommendations(
                        seed_track['id'],
                        user_id=test_user.id,
                        limit=NEXT_BATCH_SIZE
                    )
                    
                    # Filter out songs already seen
                    seen_ids = {r['id'] for r in recommendations}
                    fresh_recs = [r for r in new_recs if r['id'] not in seen_ids]
                    next_batch_ready = fresh_recs
                    next_batch_loading = False
                    print(f"\n   ✅ Background: {len(fresh_recs)} new songs ready!")
                    
                except Exception as e:
                    print(f"\n   ⚠️  Background fetch failed: {e}")
                    next_batch_loading = False
            
            # Start background thread
            bg_thread = threading.Thread(target=fetch_in_background, daemon=True)
            bg_thread.start()
            
        except Exception as e:
            print(f"   ⚠️  Could not start background fetch: {e}")
            next_batch_loading = False
    
    # Add next batch when current batch is exhausted
    if remaining == 0 and len(next_batch_ready) > 0:
        print(f"\n✨ Seamlessly adding {len(next_batch_ready)} new personalized songs!")
        recommendations.extend(next_batch_ready)
        next_batch_ready = []
        print(f"   🎯 Keep swiping!")
    elif remaining == 0 and next_batch_loading:
        print(f"\n⏳ Waiting for background batch to finish...")
        # In real app, user would just see a brief loading indicator
        time.sleep(2)  # Give thread time to finish

# End of songs
print("\n" + "=" * 70)
print("  🎉 ALL SONGS SWIPED!")
print("=" * 70)

print(f"\n📊 Final Statistics:")
print(f"   Total Swipes: {total_swipes}")
print(f"   Likes: {likes} ({likes/total_swipes*100 if total_swipes > 0 else 0:.1f}%)")
print(f"   Passes: {dislikes} ({dislikes/total_swipes*100 if total_swipes > 0 else 0:.1f}%)")

if likes > 0:
    print(f"\n💚 Your Liked Songs:")
    liked = [s for s in swipe_history if s['direction'] == 'right']
    for i, s in enumerate(liked[-5:], 1):
        print(f"   {i}. {s['name']} (Match: {s['score']*100:.1f}%)")

print("\n🧠 Preference Learning:")
print(f"   • Algorithm updated {total_swipes // LEARN_INTERVAL} times")
print(f"   • Your taste profile is saved")
print(f"   • Future recommendations will be better!")

print("\n✅ Swipe simulation complete!")
print("   This is exactly how the real app will work!")
print("\n" + "=" * 70)

