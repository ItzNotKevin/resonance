# 🚀 Quick Test Guide

## ✅ **Both Servers Running:**
- **Backend**: `http://localhost:8000` ✅
- **Frontend**: `http://localhost:8082` ✅

## 🧪 **Test Steps:**

### **1. Open the App**
- Go to: `http://localhost:8082`
- You should see the music discovery interface

### **2. Test Search**
- Type "Taylor" in the search box
- **Wait 2-3 seconds** for results to appear
- You should see a dropdown with songs

### **3. Test Recommendations**
- Click on any song from the dropdown
- **Wait 20-30 seconds** for recommendations to load
- You should see swipeable cards

### **4. Test Swiping**
- Swipe right (like) or left (dislike)
- Cards should animate and move to next song

## 🔧 **If You Get Timeouts:**

### **Check Backend:**
```bash
curl http://localhost:8000/api/search?query=test
```
Should return JSON with songs.

### **Check Frontend:**
- Open browser console (F12)
- Look for error messages
- Should see "Searching for: ..." logs

## 🎵 **Expected Behavior:**
- ✅ Type → See instant search results
- ✅ Click song → Get recommendations
- ✅ Swipe → Next song appears
- ✅ No more 30-second timeouts!

**Your music discovery app is ready!** 🎉










