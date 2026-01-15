# Frontend "Too Many Open Files" Fix

## The Problem

macOS has a default limit of ~256 files that can be watched simultaneously. Metro bundler (React Native's file watcher) tries to watch all files in your project, which exceeds this limit.

Error:
```
Error: EMFILE: too many open files, watch
```

## The Fix

### Quick Fix (Every Time):
```bash
ulimit -n 10000
cd frontend
npx expo start
```

### Permanent Fix:

Add this to your shell profile (`~/.zshrc` or `~/.bash_profile`):

```bash
echo "ulimit -n 10000" >> ~/.zshrc
source ~/.zshrc
```

### Or Use the Helper Script:
```bash
cd frontend
./start.sh
```

This automatically sets the limit and starts Expo!

## What I Did

✅ Started frontend with increased file limit  
✅ Created `frontend/start.sh` helper script  
✅ Frontend should be running now in background  

## Check if It's Running

The frontend is starting in the background. Give it 10-20 seconds, then:

1. **Check backend is running**: http://localhost:8000
2. **Check frontend**: http://localhost:19006 (or 8081)

Or just run:
```bash
cd frontend
./start.sh
```

Then press `w` for web!

## Alternative: Use the Script From Now On

Instead of `npx expo start`, use:
```bash
cd frontend
./start.sh
```

This handles the file limit automatically! ✅












