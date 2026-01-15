# Quick Start Guide

Get the app running in 5 minutes!

## Step 1: Get API Keys (5 minutes)

### Spotify
1. Go to https://developer.spotify.com/dashboard
2. Click "Create app"
3. Name it anything, add redirect URI: `http://localhost:8000/callback`
4. Copy your **Client ID** and **Client Secret**

### Last.fm (Optional)
1. Go to https://www.last.fm/api/account/create
2. Fill the form
3. Copy your **API Key**

## Step 2: Setup Backend (3 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Mac/Linux)
source venv/bin/activate
# OR Windows:
# venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Create .env file (Mac/Linux)
cat > .env << 'EOF'
SPOTIFY_CLIENT_ID=your_id_here
SPOTIFY_CLIENT_SECRET=your_secret_here
LASTFM_API_KEY=your_key_here
LASTFM_API_SECRET=your_secret_here
JWT_SECRET=any_random_string_12345
EOF

# Edit .env and add your actual keys
nano .env  # or use any text editor
```

## Step 3: Setup Frontend (2 minutes)

```bash
cd ../frontend
npm install
```

## Step 4: Run! (1 minute)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npx expo start
```

Then press `w` for web browser!

## 🎉 Done!

Search for a song, swipe on recommendations, discover new music!

---

**Need help?** Check `SETUP_GUIDE.md` for detailed instructions.












