# 🎵 Music Swipe App - START HERE

Welcome to your music recommendation app! This guide will get you started.

## 🎯 What You Have

A fully-functional, cross-platform music discovery app that:

✅ **Searches** any song or artist via Spotify API  
✅ **Recommends** similar songs using 5 advanced algorithms  
✅ **Learns** your preferences as you swipe  
✅ **Works** on iOS, Android, and Web  
✅ **Integrates** Spotify + Last.fm for best results  
✅ **Tracks** your history (optional login)  

## 🚀 Quick Start (15 minutes)

### 1️⃣ Get API Keys (5 min)

**Spotify** (Required):
- Visit: https://developer.spotify.com/dashboard
- Create app → Copy Client ID & Secret

**Last.fm** (Optional but recommended):
- Visit: https://www.last.fm/api/account/create
- Create app → Copy API Key

### 2️⃣ Setup (5 min)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file and add your keys
# (See SETUP_GUIDE.md for detailed instructions)

# Frontend
cd ../frontend
npm install
```

### 3️⃣ Run (2 min)

**Terminal 1:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2:**
```bash
cd frontend
npx expo start
# Press 'w' for web browser
```

## 📚 Documentation

| File | Purpose |
|------|---------|
| **QUICK_START.md** | Fastest way to get running |
| **SETUP_GUIDE.md** | Step-by-step detailed setup |
| **README.md** | Complete project documentation |
| **API_DOCUMENTATION.md** | API endpoint reference |
| **CHECKLIST.md** | Verify everything works |
| **PROJECT_STRUCTURE.md** | File organization guide |
| **IMPLEMENTATION_SUMMARY.md** | Technical deep-dive |

## 🎨 How It Works

1. **Search** for any song or artist
2. App fetches audio features from Spotify
3. Algorithm finds 50+ similar songs using:
   - Audio feature similarity (cosine, euclidean, manhattan)
   - Genre/tag matching (Jaccard)
   - Community wisdom (Last.fm)
   - Era matching
   - Popularity optimization
4. **Swipe Right** to like, **Left** to pass
5. App learns your taste and improves recommendations

## 🔧 Tech Stack

**Backend**: Python, FastAPI, Spotify API, Last.fm API, SQLite  
**Frontend**: React Native, Expo, TypeScript, React Navigation  
**Algorithm**: 5 similarity methods + adaptive learning  
**Audio Analysis**: Feature Fusion (Librosa + Deezer + AcousticBrainz + MusicBrainz)  

## 📱 Testing Options

- **Web**: Easiest, press `w` in Expo
- **Phone**: Install Expo Go, scan QR code
- **Simulator**: iOS (Mac) or Android emulator

## ⚠️ Important Notes

1. **Must create `.env` file** in `backend/` with your API keys
2. **Last.fm is optional** - app works with just Spotify
3. **Guest mode works** - no login required to use app
4. **First search** may be slow (API cold start)
5. **Some songs** don't have 30s previews (Spotify limitation)

## 🐛 Troubleshooting

**"Cannot connect to backend"**
- Ensure backend is running at http://localhost:8000
- Check browser console for errors

**"No recommendations found"**
- Verify Spotify credentials in `.env`
- Check backend terminal for error messages

**"Module not found"**
- Backend: `pip install -r requirements.txt`
- Frontend: `npm install`

## 🎯 Next Steps

1. ✅ Follow **QUICK_START.md** to get running
2. ✅ Search for your favorite song
3. ✅ Start swiping!
4. ✅ Create an account to save preferences
5. ✅ Swipe 20+ songs to see adaptive learning in action

## 🌟 Features to Explore

- **Audio Previews**: Tap play button on cards
- **Match Scores**: See similarity percentage
- **Profile Stats**: Track your swipe history
- **Genre Tags**: Discover by genre/mood
- **Adaptive Learning**: Gets better as you swipe

## 📞 Need Help?

1. Check **SETUP_GUIDE.md** for detailed instructions
2. Review **CHECKLIST.md** to verify setup
3. Read **API_DOCUMENTATION.md** for technical details
4. Check **TROUBLESHOOTING** section in README.md

## 🎉 Ready?

Open **QUICK_START.md** and let's get this running!

---

**Made with**: FastAPI ⚡ React Native 📱 Spotify 🎵 Last.fm 🎧 Love ❤️

