# Quick Setup Guide

Follow these steps to get the Music Swipe app running on your machine.

## Step 1: Get Spotify API Credentials

1. Visit https://developer.spotify.com/dashboard
2. Click "Log in" (or "Sign up" if you don't have a Spotify account)
3. Click "Create app" button
4. Fill in the form:
   - **App name**: Music Swipe (or any name you like)
   - **App description**: Music recommendation app
   - **Website**: http://localhost:3000 (or leave blank)
   - **Redirect URI**: http://localhost:8000/callback
   - Check the box to agree to terms
5. Click "Save"
6. You'll see your app dashboard
7. Click "Settings" button
8. You'll see:
   - **Client ID**: (copy this)
   - **Client Secret**: Click "View client secret" and copy it

Keep these safe - you'll need them in Step 4!

## Step 2: Get Last.fm API Key (Optional but Recommended)

1. Visit https://www.last.fm/api/account/create
2. Fill in the form:
   - **Application name**: Music Swipe
   - **Application description**: Music recommendation app
   - **Application homepage**: http://localhost:3000 (or leave blank)
   - **Callback URL**: http://localhost:8000 (or leave blank)
3. Click "Submit"
4. You'll see:
   - **API Key**: (copy this)
   - **Shared secret**: (copy this)

## Step 3: Install Dependencies

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Step 4: Configure API Keys

Create a file named `.env` in the `backend/` directory:

```bash
cd backend
```

**On Mac/Linux:**
```bash
cat > .env << 'EOF'
SPOTIFY_CLIENT_ID=paste_your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=paste_your_spotify_client_secret_here
LASTFM_API_KEY=paste_your_lastfm_api_key_here
LASTFM_API_SECRET=paste_your_lastfm_secret_here
JWT_SECRET=change_this_to_any_random_string_123456
EOF
```

**On Windows (Command Prompt):**
```cmd
notepad .env
```

Then paste this content and replace with your actual keys:
```
SPOTIFY_CLIENT_ID=paste_your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=paste_your_spotify_client_secret_here
LASTFM_API_KEY=paste_your_lastfm_api_key_here
LASTFM_API_SECRET=paste_your_lastfm_secret_here
JWT_SECRET=change_this_to_any_random_string_123456
```

**Important**: Replace the placeholder values with your actual credentials!

Example of what it should look like:
```
SPOTIFY_CLIENT_ID=a1b2c3d4e5f6g7h8i9j0
SPOTIFY_CLIENT_SECRET=z9y8x7w6v5u4t3s2r1q0
LASTFM_API_KEY=1234567890abcdef1234567890abcdef
LASTFM_API_SECRET=abcdef1234567890abcdef1234567890
JWT_SECRET=my_super_secret_key_12345
```

## Step 5: Run the App

### Terminal 1 - Start Backend

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Visit http://localhost:8000 in your browser - you should see the API welcome message!

### Terminal 2 - Start Frontend

Open a NEW terminal window:

```bash
cd frontend
npx expo start
```

You should see a QR code and menu options.

### Choose How to Test:

**Option A: Web Browser (Easiest)**
- Press `w` key
- Browser opens automatically

**Option B: Phone (Best Experience)**
- Install "Expo Go" app from App Store or Google Play
- Scan the QR code with your camera (iOS) or in Expo Go app (Android)
- Make sure phone and computer are on same WiFi!

**Option C: Simulator (If you have Xcode or Android Studio)**
- Press `i` for iOS simulator (Mac only)
- Press `a` for Android emulator

## Step 6: Test It!

1. Search for a song (try "Blinding Lights")
2. Click on a result
3. Click "Start Swiping"
4. Swipe right (like) or left (pass) on songs
5. Tap the play button to hear previews!

## Troubleshooting

### "Cannot connect to backend"

1. Make sure backend is running (Terminal 1)
2. Visit http://localhost:8000 in browser - should show welcome message
3. Check that `.env` file exists in backend directory
4. If using phone, update API URL:
   - Edit `frontend/src/services/api.ts`
   - Change `localhost` to your computer's IP address
   - Find IP: 
     - Mac: System Preferences → Network
     - Windows: `ipconfig` in Command Prompt
     - Linux: `ifconfig` in Terminal

### "Spotify credentials not set"

1. Check that `.env` file exists in `backend/` directory
2. Open `.env` and verify credentials are there (no quotes needed)
3. Restart the backend server

### "Module not found" errors

**Backend:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Phone can't scan QR code

1. Ensure phone and computer are on same WiFi
2. Try tunnel mode: `npx expo start --tunnel`
3. Or just use web browser: Press `w`

## Need More Help?

Check the main README.md for detailed documentation!












