# Testing the Recommendation Algorithm

You can test the recommendation algorithm independently without running the full app!

## Quick Test (No API Keys Needed)

This tests the algorithm with sample song data:

```bash
cd backend
python test_algorithm.py
```

This will run 6 tests:
1. ✅ Feature Normalization - Converts audio features to 0-1 range
2. ✅ Feature Weighting - Applies importance weights (energy, valence, etc.)
3. ✅ Similarity Methods - Tests cosine, euclidean, manhattan distances
4. ✅ Genre Matching - Tests Jaccard similarity for tags/genres
5. ✅ Contextual Bonuses - Tests temporal & popularity adjustments
6. ✅ Full Algorithm - Complete recommendation scoring

**Example Output:**
```
TEST 6: Complete Recommendation Algorithm
==========================================

Seed song: Blinding Lights by The Weeknd

Recommendations (ranked by similarity):

1. Save Your Tears              by The Weeknd           
   Score: 0.8234 (82.3%) ████████████████

2. Levitating                   by Dua Lipa             
   Score: 0.7456 (74.6%) ██████████████

3. Wonderwall                   by Oasis                
   Score: 0.4521 (45.2%) ████████

4. Bohemian Rhapsody            by Queen                
   Score: 0.3892 (38.9%) ███████
```

## Test with Real Spotify Data

Once you have Spotify API credentials configured:

```bash
cd backend

# Make sure virtual environment is activated
source venv/bin/activate  # Windows: venv\Scripts\activate

# Test with any song
python test_algorithm.py --live "Blinding Lights"
python test_algorithm.py --live "Bohemian Rhapsody"
python test_algorithm.py --live "your favorite song"
```

This will:
1. Search Spotify for the song
2. Get real audio features
3. Generate actual recommendations
4. Show top 10 similar songs with match percentages

## What Gets Tested

### Feature Normalization
Converts raw Spotify features to normalized 0-1 range:
- Acousticness, danceability, energy (already 0-1)
- Loudness: -60 to 0 dB → 0-1
- Tempo: 40-200 BPM → 0-1
- Duration: 30s to 10min → 0-1

### Feature Importance
Research-backed weights for perceptually important features:
- Energy & Valence: 1.5x (most important - mood/vibe)
- Danceability: 1.3x
- Tempo: 1.2x
- Key: 0.6x (least important)

### Similarity Algorithms
- **Cosine (35%)**: Angular distance between feature vectors
- **Euclidean (15%)**: Straight-line distance
- **Manhattan (10%)**: Sum of absolute differences
- **Jaccard (20%)**: Genre/tag overlap
- **Last.fm (15%)**: Community wisdom
- **Bonuses (5%)**: Temporal era + popularity

### Sample Test Data

The script includes realistic test data:
- **Seed**: Blinding Lights (The Weeknd) - High energy pop
- **Similar**: Save Your Tears - Should score ~80-85%
- **Somewhat Similar**: Levitating - Should score ~70-75%
- **Different Era**: Wonderwall - Should score ~40-50%
- **Very Different**: Bohemian Rhapsody - Should score ~35-40%

## Expected Results

✅ **Good signs:**
- Similar songs score 70-90%
- Different genres score 30-50%
- All scores between 0-1
- Rankings make musical sense

❌ **Problems to watch for:**
- All songs score the same → Check weighting
- Scores outside 0-1 → Check normalization
- Random rankings → Check similarity calculations

## Understanding the Output

Each test shows:
- Raw → Normalized values
- Feature weights applied
- Individual similarity scores
- Combined final scores
- Ranked recommendations

## Troubleshooting

**Error: "No module named 'recommendation_engine'"**
- Make sure you're in the `backend/` directory

**Error: "Spotify credentials not set"**
- Only affects `--live` mode
- Sample data tests work without credentials

**Error: "No module named 'numpy'"**
- Install dependencies: `pip install -r requirements.txt`

## Next Steps

After confirming the algorithm works:

1. ✅ Algorithm tested with sample data
2. Set up Spotify credentials (see SETUP_GUIDE.md)
3. Test with `--live` mode
4. Run full backend: `uvicorn main:app --reload`
5. Test frontend: `cd frontend && npx expo start`

## Technical Details

The algorithm uses a weighted ensemble approach:

```
Final Score = 
  60% × (35% cosine + 15% euclidean + 10% manhattan) +
  20% × jaccard(genres/tags) +
  15% × last.fm_score +
  2.5% × temporal_similarity +
  2.5% × popularity_adjustment
```

This combines:
- Objective audio analysis (60%)
- Subjective genre matching (20%)
- Community wisdom (15%)
- Discovery optimization (5%)

The result is a score from 0-1 where:
- 0.9-1.0 = Extremely similar (rare)
- 0.7-0.9 = Very similar (great recommendations)
- 0.5-0.7 = Somewhat similar (decent matches)
- 0.3-0.5 = Different but related
- 0.0-0.3 = Very different (unlikely to recommend)












