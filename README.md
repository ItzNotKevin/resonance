# Music Swipe Recommendation App

A cross-platform music discovery app that helps users find similar songs using a Tinder-style swipe interface. The app leverages Spotify and Last.fm APIs, audio feature analysis, and machine learning algorithms to provide personalized recommendations that adapt to user preferences.

## Features

- **Smart Search**: Search for any song or artist to start discovering similar music
- **Swipe Interface**: Intuitive Tinder-style card swipes (right for like, left for pass)
- **Advanced Recommendation Algorithm**:
  - Cosine similarity for overall feature matching
  - Euclidean and Manhattan distance for precise similarity
  - Jaccard similarity for genre/tag matching
  - Temporal similarity (songs from similar eras)
  - Popularity adjustments (discover hidden gems)
  - Last.fm community wisdom integration
- **Adaptive Learning**: Recommendations improve based on your swipe history
- **Optional Authentication**: Save your preferences and swipe history across sessions
- **Cross-Platform**: Works on iOS, Android, and Web

## Tech Stack

**Frontend**: React Native with Expo, TypeScript, React Native Web
**Backend**: Python with FastAPI
**Database**: SQLite
**APIs**: Spotify Web API, Last.fm API

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.10 or higher)
- npm or yarn
- Spotify Developer Account
- Last.fm API Account (optional but recommended)

## Getting Started

### 1. Clone the Repository

```bash
cd musicapp
```

### 2. Get API Credentials

#### Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create app"
4. Fill in:
   - App name: "Music Swipe App" (or any name)
   - App description: "Music recommendation app"
   - Redirect URI: `http://localhost:8000/callback`
5. Accept terms and click "Save"
6. You'll see your **Client ID** and **Client Secret**

#### Last.fm API Key

1. Go to [Last.fm API Account Creation](https://www.last.fm/api/account/create)
2. Fill in:
   - Application name: "Music Swipe App"
   - Application description: "Music recommendation app"
3. Click "Submit"
4. You'll receive your **API Key** and **Shared Secret**

### 3. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
LASTFM_API_KEY=your_lastfm_api_key_here
LASTFM_API_SECRET=your_lastfm_secret_here
JWT_SECRET=your-random-secret-key-change-this
EOF

# Edit .env and add your actual credentials
# On macOS: open .env
# On Linux: nano .env
# On Windows: notepad .env
```

**Important**: Replace the placeholder values in `.env` with your actual API credentials!

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# For iOS development (Mac only), also run:
# cd ios && pod install && cd ..
```

### 5. Running the App

#### Start the Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload
```

The backend will be running at `http://localhost:8000`

#### Start the Frontend

In a new terminal:

```bash
cd frontend
npx expo start
```

#### Testing Options

1. **Web Browser** (Easiest):
   - Press `w` in the Expo CLI
   - Opens in your default browser

2. **iOS Simulator** (Mac only):
   - Press `i` in the Expo CLI
   - Requires Xcode installed

3. **Android Emulator**:
   - Press `a` in the Expo CLI
   - Requires Android Studio installed

4. **Physical Device** (Best for mobile):
   - Install "Expo Go" app from App Store or Google Play
   - Scan the QR code shown in terminal
   - **Note**: Your phone and computer must be on the same WiFi network
   - If using physical device, update the API URL:
     - Open `frontend/src/services/api.ts`
     - Change `http://localhost:8000/api` to `http://YOUR_COMPUTER_IP:8000/api`
     - Find your IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)

## How to Use

1. **Search for a Song**: Enter a song name or artist in the search bar
2. **Select a Seed**: Click on a song from the results
3. **Start Swiping**: Tap "Start Swiping" to get recommendations
4. **Swipe Right**: Like a song (helps personalize future recommendations)
5. **Swipe Left**: Pass on a song
6. **Play Preview**: Tap the play button on cards to hear a 30-second preview
7. **Optional Login**: Create an account to save your preferences across sessions

## Project Structure

```
musicapp/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration and settings
│   ├── database.py             # SQLite database models
│   ├── models.py               # Pydantic data models
│   ├── spotify_client.py       # Spotify API integration
│   ├── lastfm_client.py        # Last.fm API integration
│   ├── recommendation_engine.py # Similarity algorithms
│   └── routes/                 # API endpoints
│       ├── search.py
│       ├── recommendations.py
│       └── user.py
├── frontend/
│   ├── App.tsx                 # Root component
│   ├── src/
│   │   ├── screens/            # Main screens
│   │   ├── components/         # Reusable components
│   │   ├── services/           # API client
│   │   ├── types/              # TypeScript types
│   │   └── navigation/         # Navigation config
│   └── package.json
└── README.md
```

## API Endpoints

### Search
- `GET /api/search?query=<song_name>` - Search for tracks

### Recommendations
- `POST /api/recommendations` - Get personalized recommendations
  ```json
  {
    "seed_id": "spotify_track_id",
    "user_id": 123  // optional
  }
  ```

### User Actions
- `POST /api/swipe` - Record a swipe (like/dislike)
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `GET /api/user/preferences/{user_id}` - Get user stats

## Algorithm Details

### Similarity Calculation

The recommendation engine uses a sophisticated multi-factor approach:

1. **Audio Feature Analysis (45%)**:
   - Cosine similarity (27%): Angular distance between feature vectors
   - Euclidean distance (11%): Straight-line distance
   - Manhattan distance (7%): Sum of absolute differences
   - Features analyzed: energy, valence, danceability, tempo, acousticness, instrumentalness, speechiness, liveness, loudness, key, duration

2. **Community Wisdom (30%)**:
   - Last.fm similar tracks score
   - Based on millions of user listening patterns
   - Highest weight for proven community recommendations

3. **Genre/Tag Matching (20%)**:
   - Jaccard similarity on Spotify genres + Last.fm tags
   - Matches user's input vibe with community tags

4. **Contextual Bonuses (5%)**:
   - Temporal similarity: Songs from similar eras
   - Popularity adjustment: Balances familiarity with discovery

### Adaptive Learning

After every 10 swipes, the system:
- Calculates average features of liked songs
- Adjusts feature weights based on user preferences
- Filters out songs similar to rejected ones
- Re-ranks recommendations using learned preferences

## Troubleshooting

### Backend Issues

**"Spotify credentials not set"**
- Make sure you created the `.env` file in the `backend/` directory
- Verify your Spotify Client ID and Secret are correct
- Restart the backend server after updating `.env`

**"Database error"**
- Delete `backend/musicapp.db` and restart the server to recreate the database

### Frontend Issues

**"Network Error" or "Failed to load recommendations"**
- Ensure backend is running (`http://localhost:8000`)
- Check if you can access `http://localhost:8000` in your browser
- If using physical device, update API URL to your computer's IP address

**"Expo Go can't connect"**
- Ensure phone and computer are on the same WiFi network
- Try running `npx expo start --tunnel` for a different connection method

**Swipe gestures not working on web**
- Use mouse drag instead of touch
- Or use keyboard: Left Arrow = pass, Right Arrow = like

## Future Enhancements

- [ ] Apple Music API integration
- [ ] LLM-based lyric analysis for semantic similarity
- [ ] Playlist generation from liked songs
- [ ] Social features (share discoveries with friends)
- [ ] Advanced filters (year, genre, mood)
- [ ] Export liked songs to Spotify playlists
- [ ] Dark mode
- [ ] Song lyrics display

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is for educational and personal use. Ensure you comply with Spotify and Last.fm API terms of service.

## Acknowledgments

- Spotify Web API for music data and audio features
- Last.fm API for community-based recommendations
- React Native and Expo for cross-platform development
- FastAPI for the elegant Python backend framework

