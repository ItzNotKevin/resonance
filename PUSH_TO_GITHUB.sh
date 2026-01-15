#!/bin/bash
# Script to push code to GitHub repository: resonance

# Navigate to project directory
cd /Users/kevinli/musicapp

# Initialize git (if not already done)
git init

# Add all files (respects .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: Music discovery app with swipe interface and AI recommendations"

# Add GitHub remote
git remote add origin https://github.com/ItzNotKevin/resonance.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main

echo "✅ Code pushed to GitHub successfully!"
