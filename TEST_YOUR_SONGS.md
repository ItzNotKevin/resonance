# Test the Algorithm with Your Own Songs! 🎵

This guide shows you how to test the recommendation algorithm with any song you want and see real similarity scores.

## Quick Start

### 1. Setup (First Time Only)

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Add Spotify Credentials

Create a file `backend/.env`:

```bash
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
LASTFM_API_KEY=your_lastfm_key_here  # Optional
```

**Get Spotify credentials:**
1. Visit https://developer.spotify.com/dashboard
2. Click "Create app"
3. Copy your Client ID and Secret
4. Paste them in `.env`

See **SETUP_GUIDE.md** for detailed instructions.

### 3. Run Interactive Tester

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python interactive_test.py
```

## What You Can Do

### 🔍 Search Any Song
```
Search for a song: blinding lights

Found 10 results:

 1. Blinding Lights                 by The Weeknd                    [95]
 2. Blinding Lights - Remix         by The Weeknd, Rosalía          [88]
 ...

Select a song (1-10): 1
```

### 📊 See Audio Features
```
Audio Features: Blinding Lights

Musical Characteristics:
  Energy:          ████████████████     0.73
  Danceability:    ██████████           0.51
  Valence (mood):  ██████               0.33
  Acousticness:    ░                    0.00
  Instrumentals:   ░                    0.00

Audio Properties:
  Tempo:           171.0 BPM
  Loudness:        -5.9 dB
  Duration:        200 seconds
  Key:             1 (C#)
```

### 🎯 Get Recommendations with Scores
```
TOP 20 RECOMMENDATIONS
======================================

 1. Save Your Tears              by The Weeknd        
    Match:  82.3% ████████████████

 2. In Your Eyes                 by The Weeknd        
    Match:  79.8% ███████████████

 3. Levitating                   by Dua Lipa          
    Match:  74.5% ██████████████

 4. Don't Start Now              by Dua Lipa          
    Match:  72.1% ██████████████
```

### 🔬 See Detailed Breakdown
For the top match, you'll see:
- **Score Components**: How each algorithm contributed
- **Audio Features**: Cosine, Euclidean, Manhattan similarities
- **Genre Matching**: Jaccard similarity for tags
- **Last.fm Score**: Community wisdom
- **Era Matching**: Temporal similarity
- **Popularity**: Discovery optimization
- **Feature Comparison**: Side-by-side comparison of audio features

```
DETAILED BREAKDOWN - TOP RECOMMENDATION
======================================

Save Your Tears by The Weeknd
Overall Match: 82.3%

Score Components:
  🎵 Audio Features (60%):  0.4912
     - Cosine similarity:    0.9234
     - Euclidean distance:   0.8456
     - Manhattan distance:   0.8123

  🏷️  Genre/Tags (20%):     0.8500
     - Common tags: ['pop', 'canadian pop', 'electronic']

  👥 Last.fm Score (15%):   0.9500

  📅 Era Match (2.5%):      1.0000
     - Seed: 2019, This: 2020

  ⭐ Popularity (2.5%):     1.0000
     - Popularity: 92/100

Feature Comparison:
Feature              Seed      Match       Diff
----------------------------------------------------
energy              0.730      0.827      0.097
valence             0.334      0.428      0.094
danceability        0.514      0.672      0.158
tempo             171.0      118.1       52.9
acousticness        0.001      0.036      0.035
```

## Example Sessions

### Example 1: Find Songs Like "Bohemian Rhapsody"
```bash
python interactive_test.py

Search for a song: bohemian rhapsody
Select: 1

[See audio features - high energy, complex structure]

Generate recommendations? Y

Top matches:
- Don't Stop Me Now (Queen) - 76.2%
- Somebody to Love (Queen) - 73.8%
- We Are the Champions (Queen) - 71.5%
```

### Example 2: Discover Similar Lo-Fi
```bash
Search for a song: lofi hip hop

[Pick a chill lo-fi track]

Top matches:
- Other lo-fi tracks
- Jazz hop beats
- Chill study music
All with high acousticness, low energy
```

### Example 3: Compare Similarity Scores
```bash
# Test 1
Search: "rap god" by Eminem
Top match: Fast rap with high speechiness

# Test 2  
Search: "wonderwall" by Oasis
Top match: Alternative rock, similar tempo

# Compare how different genres get different scores!
```

## Understanding the Scores

| Score Range | Meaning | What to Expect |
|-------------|---------|----------------|
| 85-100% | Extremely Similar | Same artist, album, or very close style |
| 70-85% | Very Similar | Great recommendations, similar vibe |
| 55-70% | Somewhat Similar | Same genre/mood, worth exploring |
| 40-55% | Related | Different but shares some characteristics |
| 0-40% | Different | Different genre/era/style |

## Tips for Testing

1. **Try different genres** to see how the algorithm adapts
2. **Compare songs from same artist** - should score high
3. **Test across eras** - see temporal similarity in action
4. **Look at feature differences** - understand why songs match
5. **Check genre tags** - see how Jaccard similarity works

## What Gets Analyzed

For each song, the algorithm examines:

**Audio Features (60% of score):**
- Energy, valence (mood), danceability
- Tempo, key, loudness
- Acousticness, instrumentalness, speechiness

**Genres/Tags (20%):**
- Spotify genres
- Last.fm tags (if available)

**Community Data (15%):**
- Last.fm similar track scores
- Listening patterns from millions of users

**Context (5%):**
- Release year (songs from same era)
- Popularity (sweet spot 40-70%)

## Troubleshooting

**"Spotify API credentials not found"**
- Create `backend/.env` file
- Add your credentials
- See SETUP_GUIDE.md for help

**"No module named 'numpy'"**
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

**"Could not connect to Spotify API"**
- Check your credentials are correct
- No quotes needed in .env file
- Make sure you copied the full Client Secret

**Recommendations seem random**
- Last.fm is optional but improves results
- Algorithm works best with popular songs
- Some niche tracks may have limited metadata

## Next Steps

Once you're happy with the algorithm:

1. ✅ Recommendations look good
2. ✅ Similarity scores make sense
3. ✅ Different genres work correctly
4. Ready to run the full app!

Follow **QUICK_START.md** to launch the complete app with the swipe interface.

## Command Reference

```bash
# Run interactive tester
python interactive_test.py

# Run algorithm tests (no API needed)
python test_algorithm.py

# Run with specific song (old way)
python test_algorithm.py --live "song name"

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

Have fun discovering music! 🎵












