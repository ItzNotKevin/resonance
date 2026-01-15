# API Documentation

Complete reference for the Music Swipe Recommendation API.

## Base URL

```
http://localhost:8000
```

## Authentication

Most endpoints work without authentication. Authentication is optional and only needed for saving user preferences.

### Register

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user_id": 123
}
```

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user_id": 123
}
```

## Search

### Search Tracks

Search for songs by name or artist.

```http
GET /api/search?query={search_term}&limit={number}
```

**Parameters:**
- `query` (required): Search term (song name or artist)
- `limit` (optional): Number of results (default: 20)

**Example:**
```http
GET /api/search?query=blinding%20lights&limit=10
```

**Response:**
```json
[
  {
    "id": "0VjIjW4GlUZAMYd2vXMi3b",
    "name": "Blinding Lights",
    "artist": "The Weeknd",
    "album": "After Hours",
    "image_url": "https://i.scdn.co/image/...",
    "preview_url": "https://p.scdn.co/mp3-preview/...",
    "popularity": 95
  }
]
```

## Recommendations

### Get Recommendations

Get personalized song recommendations based on a seed track.

```http
POST /api/recommendations
Content-Type: application/json

{
  "seed_id": "string",
  "user_id": 123  // optional
}
```

**Request Body:**
- `seed_id` (required): Spotify track ID
- `user_id` (optional): User ID for personalized recommendations

**Example:**
```json
{
  "seed_id": "0VjIjW4GlUZAMYd2vXMi3b",
  "user_id": 5
}
```

**Response:**
```json
[
  {
    "id": "1301WleyT98MSxVHPZCA6M",
    "name": "Save Your Tears",
    "artist": "The Weeknd",
    "album": "After Hours",
    "image_url": "https://i.scdn.co/image/...",
    "preview_url": "https://p.scdn.co/mp3-preview/...",
    "audio_features": {
      "acousticness": 0.0359,
      "danceability": 0.672,
      "energy": 0.827,
      "instrumentalness": 0.000234,
      "liveness": 0.0938,
      "loudness": -4.868,
      "speechiness": 0.0504,
      "tempo": 118.051,
      "valence": 0.428,
      "duration_ms": 215627,
      "key": 0
    },
    "metadata": {
      "genres": ["canadian contemporary r&b", "canadian pop"],
      "lastfm_tags": ["pop", "electronic", "synth-pop"],
      "release_year": 2020,
      "popularity": 92,
      "lastfm_similarity": 0.85
    },
    "similarity_score": 0.923
  }
]
```

## User Actions

### Record Swipe

Record a user's swipe action (like or dislike).

```http
POST /api/swipe
Content-Type: application/json

{
  "user_id": 123,  // optional
  "song_id": "string",
  "song_name": "string",
  "artist_name": "string",
  "direction": "left|right",
  "audio_features": {},
  "metadata": {}
}
```

**Request Body:**
- `user_id` (optional): User ID (if logged in)
- `song_id` (required): Spotify track ID
- `song_name` (required): Song name
- `artist_name` (required): Artist name
- `direction` (required): "left" for dislike, "right" for like
- `audio_features` (required): Audio features object
- `metadata` (required): Metadata object

**Response:**
```json
{
  "status": "success",
  "message": "Swipe recorded"
}
```

### Get User Preferences

Get user's swipe statistics and learned preferences.

```http
GET /api/user/preferences/{user_id}
```

**Parameters:**
- `user_id` (required): User ID

**Response:**
```json
{
  "username": "john_doe",
  "total_swipes": 150,
  "likes": 85,
  "dislikes": 65,
  "recent_swipes": [
    {
      "song_name": "Blinding Lights",
      "artist_name": "The Weeknd",
      "direction": "right",
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "preferences": {
    "preferred_genres": ["pop", "electronic", "synth-pop"],
    "feature_weights": {
      "energy": 1.8,
      "valence": 1.3,
      "danceability": 1.5,
      "tempo": 1.2,
      "acousticness": 0.7
    }
  }
}
```

## Audio Features Explained

The Spotify API provides these audio features for each track:

- **acousticness** (0-1): Confidence that track is acoustic
- **danceability** (0-1): How suitable for dancing
- **energy** (0-1): Intensity and activity level
- **instrumentalness** (0-1): Predicts if track has no vocals
- **liveness** (0-1): Presence of audience in recording
- **loudness** (-60 to 0 dB): Overall loudness
- **speechiness** (0-1): Presence of spoken words
- **tempo** (BPM): Estimated tempo
- **valence** (0-1): Musical positiveness (happy vs sad)
- **duration_ms**: Length in milliseconds
- **key** (0-11): Pitch class (0=C, 1=C♯, etc.)

## Similarity Algorithm

The recommendation score (0-1) is calculated as:

```
final_score = 
  0.45 * feature_similarity +    // Cosine (27%), Euclidean (11%), Manhattan (7%)
  0.30 * lastfm_similarity +     // Community wisdom (highest weight)
  0.20 * jaccard_similarity +    // Genre/tag matching
  0.025 * temporal_similarity +  // Era matching
  0.025 * popularity_adjustment  // Discovery optimization
```

Higher scores indicate more similar songs.

## Error Responses

All endpoints may return these error formats:

```json
{
  "detail": "Error message here"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid credentials)
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

The API relies on Spotify and Last.fm APIs which have their own rate limits:
- **Spotify**: ~180 requests per minute
- **Last.fm**: 5 requests per second

The backend handles these limits gracefully by caching and batching requests.

## Development Tips

1. **Testing**: Use tools like Postman or curl for API testing
2. **CORS**: CORS is enabled for all origins in development
3. **Database**: SQLite file is created at `backend/musicapp.db`
4. **Logs**: Check terminal output for detailed request/response logs
5. **Debug**: Set `logging.basicConfig(level=logging.DEBUG)` in `main.py`

