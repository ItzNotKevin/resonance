# Running Your Music Swipe App 🎵

## Prerequisites ✅

You already have:
- ✅ Backend setup complete
- ✅ Frontend dependencies installed
- ✅ API credentials configured
- ✅ Algorithm tested and working

## Step 1: Start the Backend

Open a terminal and run:

```bash
cd /Users/kevinli/musicapp/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Keep this terminal running!**

Test it works: Open http://localhost:8000 in your browser
You should see: `{"message": "Music Swipe Recommendation API", ...}`

## Step 2: Start the Frontend

Open a **NEW terminal** and run:

```bash
cd /Users/kevinli/musicapp/frontend
npx expo start
```

You'll see:
```
› Metro waiting on exp://...
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)

› Press a │ open Android
› Press i │ open iOS simulator
› Press w │ open web

› Press r │ reload app
› Press m │ toggle menu
```

## Step 3: Choose How to Test

### Option A: Web Browser (Easiest!)
Press `w` key

Browser opens automatically at http://localhost:19006

**Recommended for first test!**

### Option B: Phone (Best Experience)
1. Install "Expo Go" app from App Store or Google Play
2. Scan the QR code with your camera (iOS) or in Expo Go app (Android)
3. **Important**: Phone and computer must be on same WiFi!

### Option C: iOS Simulator (Mac only)
Press `i` key

Requires Xcode installed

### Option D: Android Emulator
Press `a` key

Requires Android Studio installed

## Step 4: Use the App!

### In the App:

1. **Search Screen** (Home):
   - Search for any song or artist
   - See results
   - Click on a song
   - Tap "Start Swiping"

2. **Loading** (~20-30 seconds):
   - "Finding your perfect matches..."
   - Backend queries Last.fm, Deezer, etc.
   - Be patient!

3. **Swipe Screen**:
   - ✅ Cards appear!
   - Swipe **RIGHT** (or tap heart ❤️) = Like
   - Swipe **LEFT** (or tap X ❌) = Pass
   - Tap **play button** = Listen to 30s preview
   - See match score on each card

4. **Algorithm Learning**:
   - Every 10 swipes → learns your taste
   - When 10 cards left → fetches more automatically
   - Recommendations improve as you swipe!

5. **Optional Login**:
   - Tap "Sign In" at top
   - Create account to save preferences
   - Or skip and use as guest!

## Troubleshooting

### "Cannot connect to backend"

**Web Browser:**
- Make sure backend is running at http://localhost:8000
- Check backend terminal for errors

**Phone:**
- Update API URL in `frontend/src/services/api.ts`
- Change `localhost` to your computer's IP address
- Find IP: System Preferences → Network (Mac)
- Example: Change to `http://192.168.1.100:8000/api`

### "Loading takes too long"

- First load takes 20-30 seconds (this is normal!)
- Backend is querying Last.fm for similar tracks
- Shows loading message with timer
- Subsequent batches load in background (seamless!)

### "No preview available"

- Some songs don't have 30s previews (Spotify limitation)
- Card will still show, preview button just won't play
- This is normal!

### Frontend won't start

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npx expo start
```

## Expected First Run Experience

```
1. Open app → See "Music Swipe" search screen
2. Search "Blinding Lights" → See results
3. Click first result → Select seed
4. Tap "Start Swiping" → Loading screen (20-30s)
5. First card appears! → Start swiping
6. Swipe 10 cards → "Preferences updated!" toast
7. Keep swiping → When 10 cards left, new batch loads in background
8. Seamless infinite scroll! 🎉
```

## Features to Test

✅ **Search** - Any song or artist  
✅ **Recommendations** - 8 APIs working together!  
✅ **Swipe gestures** - Left/right or buttons  
✅ **Audio preview** - 30-second clips (if available)  
✅ **Match scores** - See similarity percentage  
✅ **Genre tags** - See why songs match  
✅ **Progressive loading** - Batches load seamlessly  
✅ **Adaptive learning** - Improves every 10 swipes  
✅ **Profile stats** - See your swipe history (if logged in)  

## Performance

- **Initial load**: 20-30 seconds
- **Swipe response**: Instant
- **Next batch**: Loads in background (you keep swiping!)
- **Learning update**: Instant
- **Preview playback**: 1-2 seconds to start

## Architecture

```
Frontend (React Native/Expo)
  Port: 19006 (web) or Expo Go app
    ↓ HTTP requests
Backend (FastAPI)
  Port: 8000
    ↓ API calls
External APIs:
  - Spotify (search)
  - Last.fm (recommendations - 30%!)
  - Deezer (audio features)
  - AcousticBrainz (audio features)
  - Genius (lyric themes)
```

## Quick Reference

### Backend Commands:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Frontend Commands:
```bash
cd frontend
npx expo start
# Then press 'w' for web
```

### Test Commands:
```bash
cd backend
python test_all_apis.py        # Test all API connections
python test_fast_recs.py        # Test fast recommendations
python swipe_simulator.py       # Test swipe experience in terminal
```

## Ready to Go! 🚀

You now have a **fully functional, cross-platform music recommendation app** with:
- Professional-grade algorithm
- 8 API integrations
- Progressive loading
- Adaptive learning
- Beautiful UI

**Start both servers and enjoy!** 🎵



