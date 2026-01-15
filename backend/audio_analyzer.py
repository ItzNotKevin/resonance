"""
Audio Feature Extraction using Librosa
Analyzes actual audio files to extract features similar to Spotify
"""

import librosa
import numpy as np
import requests
from typing import Optional, Dict
import tempfile
import logging

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """Extract audio features from audio files using Librosa"""
    
    @staticmethod
    def download_preview(preview_url: str) -> Optional[str]:
        """Download audio preview to temporary file"""
        try:
            response = requests.get(preview_url, timeout=10)
            if response.status_code == 200:
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_file.write(response.content)
                temp_file.close()
                return temp_file.name
            return None
        except Exception as e:
            logger.error(f"Error downloading preview: {e}")
            return None
    
    @staticmethod
    def extract_features(audio_path: str) -> Optional[Dict]:
        """
        Extract audio features from file
        Returns Spotify-compatible feature dict
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, duration=30)  # 30 second preview
            
            # Tempo and Beat
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            # Spectral Features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # Zero Crossing Rate (speech-like quality)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            
            # MFCCs (timbre)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # RMS Energy
            rms = librosa.feature.rms(y=y)[0]
            
            # Chroma (key/pitch)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # Calculate features in Spotify-compatible format
            
            # Energy: RMS energy normalized
            energy = float(np.mean(rms))
            energy = min(1.0, max(0.0, energy * 2))  # Normalize to 0-1
            
            # Danceability: Based on beat strength and tempo
            beat_strength = float(np.mean([beats[i+1] - beats[i] for i in range(len(beats)-1)]))
            danceability = min(1.0, max(0.0, 1 - (abs(120 - tempo) / 120)))
            
            # Valence (mood): Based on spectral features and energy
            # Higher spectral centroid + energy often = happier
            valence = float((np.mean(spectral_centroids) / np.max(spectral_centroids) + energy) / 2)
            valence = min(1.0, max(0.0, valence))
            
            # Acousticness: Inverse of spectral complexity
            spectral_complexity = float(np.std(spectral_centroids))
            acousticness = max(0.0, 1 - (spectral_complexity / 1000))
            
            # Instrumentalness: Based on spectral features (less variation = more instrumental)
            vocal_detection = float(np.mean(mfccs[1]))  # Rough vocal detection
            instrumentalness = max(0.0, 1 - abs(vocal_detection) / 20)
            
            # Speechiness: High zero-crossing rate indicates speech
            speechiness = float(np.mean(zcr))
            speechiness = min(1.0, max(0.0, speechiness * 2))
            
            # Liveness: Based on spectral flux and variance
            spectral_flux = float(np.mean(np.diff(spectral_centroids)))
            liveness = min(0.5, max(0.0, abs(spectral_flux) / 100))
            
            # Loudness: RMS in dB
            loudness = float(20 * np.log10(np.mean(rms) + 1e-6))
            loudness = max(-60, min(0, loudness))
            
            # Key: Dominant chroma
            key = int(np.argmax(np.mean(chroma, axis=1)))
            
            # Duration
            duration_ms = int(len(y) / sr * 1000)
            
            return {
                'acousticness': acousticness,
                'danceability': danceability,
                'energy': energy,
                'instrumentalness': instrumentalness,
                'liveness': liveness,
                'loudness': loudness,
                'speechiness': speechiness,
                'tempo': float(tempo),
                'valence': valence,
                'duration_ms': duration_ms,
                'key': key
            }
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None
    
    @classmethod
    def analyze_preview_url(cls, preview_url: str) -> Optional[Dict]:
        """
        Download and analyze audio from preview URL
        Main method to use
        """
        if not preview_url:
            return None
        
        # Download preview
        audio_path = cls.download_preview(preview_url)
        if not audio_path:
            return None
        
        # Extract features
        features = cls.extract_features(audio_path)
        
        # Clean up temp file
        try:
            import os
            os.unlink(audio_path)
        except:
            pass
        
        return features


# Global instance
audio_analyzer = AudioAnalyzer()












