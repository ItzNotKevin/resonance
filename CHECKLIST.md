# Pre-Launch Checklist

Use this checklist to ensure everything is set up correctly before running the app.

## ✅ Prerequisites

- [ ] Node.js v18+ installed (`node --version`)
- [ ] Python 3.10+ installed (`python --version` or `python3 --version`)
- [ ] npm or yarn installed (`npm --version`)
- [ ] Git installed (optional)

## ✅ API Credentials

- [ ] Created Spotify Developer account
- [ ] Created Spotify app in dashboard
- [ ] Copied Spotify Client ID
- [ ] Copied Spotify Client Secret
- [ ] Created Last.fm API account (optional but recommended)
- [ ] Copied Last.fm API Key
- [ ] Copied Last.fm Shared Secret

## ✅ Backend Setup

- [ ] Navigated to `backend/` directory
- [ ] Created Python virtual environment (`python -m venv venv`)
- [ ] Activated virtual environment
  - Mac/Linux: `source venv/bin/activate`
  - Windows: `venv\Scripts\activate`
- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Created `.env` file in `backend/` directory
- [ ] Added Spotify credentials to `.env`
- [ ] Added Last.fm credentials to `.env` (or left empty)
- [ ] Added JWT_SECRET to `.env`

## ✅ Frontend Setup

- [ ] Navigated to `frontend/` directory
- [ ] Installed dependencies (`npm install`)
- [ ] No errors during installation

## ✅ Running the App

- [ ] Started backend server (`uvicorn main:app --reload`)
- [ ] Backend running on http://localhost:8000
- [ ] Visited http://localhost:8000 in browser - saw welcome message
- [ ] Started frontend (`npx expo start`)
- [ ] Expo DevTools opened successfully
- [ ] Chose testing method:
  - [ ] Web browser (pressed `w`)
  - [ ] iOS simulator (pressed `i`)
  - [ ] Android emulator (pressed `a`)
  - [ ] Physical device (scanned QR code with Expo Go)

## ✅ Testing the App

- [ ] App loaded successfully
- [ ] Search for a song works
- [ ] Selected a song from results
- [ ] Clicked "Start Swiping"
- [ ] Recommendations loaded
- [ ] Swipe gestures work
- [ ] Preview play button works (if available)
- [ ] No console errors

## ✅ Optional: Authentication

- [ ] Created account (Sign Up)
- [ ] Logged in successfully
- [ ] Profile page shows statistics
- [ ] Swipes are being tracked

## 🐛 Common Issues

### Backend won't start

**Error: "No module named 'fastapi'"**
- Solution: Make sure virtual environment is activated and run `pip install -r requirements.txt`

**Error: "Spotify credentials not set"**
- Solution: Check `.env` file exists in `backend/` and contains correct credentials

### Frontend won't start

**Error: "Cannot find module..."**
- Solution: Delete `node_modules` and `package-lock.json`, then run `npm install`

**Error: "Expo command not found"**
- Solution: Run `npm install -g expo-cli` or use `npx expo start`

### App can't connect to backend

**Error: "Network Error" or "Failed to fetch"**
- Solution: Ensure backend is running and accessible at http://localhost:8000
- If using physical device, update API URL in `frontend/src/services/api.ts` to your computer's IP

### No recommendations showing

**Error: "No recommendations found"**
- Solution: Check backend console for API errors. Verify Spotify credentials are correct.
- Last.fm is optional - recommendations will still work without it

## 📝 Notes

- First run will create `musicapp.db` in backend directory
- Some songs may not have preview URLs (this is normal)
- Last.fm integration is optional but improves recommendations
- Recommendations improve as you swipe more songs
- Guest mode (no login) still works and provides recommendations

## ✨ Ready to Go!

If all checkboxes are checked, you're ready to discover new music! 🎵

Search for your favorite song and start swiping!












