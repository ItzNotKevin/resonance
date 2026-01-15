"""
Feature Fusion System
Combines audio features from multiple sources for maximum accuracy
"""

from typing import Optional, Dict, List
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

logger = logging.getLogger(__name__)


class FeatureFusion:
    """Combines features from multiple sources with weighted averaging"""
    
    # Reliability weights for each source (higher = more trustworthy)
    SOURCE_WEIGHTS = {
        'spotify': 1.0,        # Gold standard (if available)
        'librosa': 0.9,        # Very accurate, analyzes actual audio
        'acousticbrainz': 0.8, # Good database of pre-computed features
        'deezer': 0.6,         # Has BPM, limited other features
        'essentia': 0.85,      # Good analysis library
    }
    
    @staticmethod
    def fetch_acousticbrainz_features(musicbrainz_id: str) -> Optional[Dict]:
        """Fetch features from AcousticBrainz database"""
        try:
            url = f"https://acousticbrainz.org/api/v1/{musicbrainz_id}/low-level"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract features from AcousticBrainz format
                return {
                    'tempo': data.get('rhythm', {}).get('bpm', 120),
                    'key': data.get('tonal', {}).get('key_key', 0),
                    'loudness': data.get('lowlevel', {}).get('average_loudness', -10),
                    'energy': min(1.0, data.get('rhythm', {}).get('beats_loudness', {}).get('mean', 0.5)),
                    # AcousticBrainz has these but in different format
                    'source': 'acousticbrainz'
                }
        except Exception as e:
            logger.debug(f"AcousticBrainz fetch failed: {e}")
        return None
    
    @staticmethod
    def fetch_deezer_features(track_name: str, artist_name: str) -> Optional[Dict]:
        """Fetch BPM from Deezer"""
        try:
            # Search Deezer
            query = f"{track_name} {artist_name}"
            response = requests.get(
                "https://api.deezer.com/search",
                params={"q": query, "limit": 1},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    track = data['data'][0]
                    track_id = track['id']
                    
                    # Get track details
                    track_response = requests.get(
                        f"https://api.deezer.com/track/{track_id}",
                        timeout=5
                    )
                    
                    if track_response.status_code == 200:
                        track_data = track_response.json()
                        bpm = track_data.get('bpm')
                        
                        if bpm:
                            # Estimate energy from BPM
                            energy = min(1.0, max(0.0, (bpm - 60) / 140))
                            
                            return {
                                'tempo': float(bpm),
                                'energy': energy,
                                'danceability': min(1.0, energy * 1.2),
                                'source': 'deezer'
                            }
        except Exception as e:
            logger.debug(f"Deezer fetch failed: {e}")
        return None
    
    @staticmethod
    def search_musicbrainz_id(track_name: str, artist_name: str) -> Optional[str]:
        """Search for MusicBrainz recording ID"""
        try:
            url = "https://musicbrainz.org/ws/2/recording"
            params = {
                'query': f'recording:"{track_name}" AND artist:"{artist_name}"',
                'fmt': 'json',
                'limit': 1
            }
            headers = {'User-Agent': 'MusicSwipeApp/1.0'}
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('recordings'):
                    return data['recordings'][0]['id']
        except Exception as e:
            logger.debug(f"MusicBrainz search failed: {e}")
        return None
    
    @classmethod
    def fetch_from_all_sources(
        cls,
        track_name: str,
        artist_name: str,
        preview_url: Optional[str] = None,
        track_id: Optional[str] = None
    ) -> Dict[str, Dict]:
        """
        Fetch features from all available sources in parallel
        Returns dict of {source_name: features}
        """
        results = {}
        
        # Use ThreadPoolExecutor to fetch from multiple sources simultaneously
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            
            # Librosa analysis (if preview URL available)
            # Disabled - crashes on some systems
            # if preview_url:
            #     try:
            #         from audio_analyzer import audio_analyzer
            #         futures['librosa'] = executor.submit(
            #             audio_analyzer.analyze_preview_url,
            #             preview_url
            #         )
            #     except Exception as e:
            #         logger.debug(f"Librosa not available: {e}")
            
            # Deezer
            futures['deezer'] = executor.submit(
                cls.fetch_deezer_features,
                track_name,
                artist_name
            )
            
            # AcousticBrainz (need MusicBrainz ID first)
            def fetch_acousticbrainz_with_search():
                mb_id = cls.search_musicbrainz_id(track_name, artist_name)
                if mb_id:
                    return cls.fetch_acousticbrainz_features(mb_id)
                return None
            
            futures['acousticbrainz'] = executor.submit(fetch_acousticbrainz_with_search)
            
            # Spotify audio_features - REMOVED by Spotify in 2024/2025
            # No longer available, so we don't try it
            
            # Collect results as they complete
            for source, future in futures.items():
                try:
                    result = future.result(timeout=10)
                    if result:
                        result['source'] = source
                        results[source] = result
                        logger.info(f"✅ Got features from {source}")
                except Exception as e:
                    logger.debug(f"Failed to get features from {source}: {e}")
        
        return results
    
    @classmethod
    def combine_features(cls, source_features: Dict[str, Dict]) -> Dict:
        """
        Combine features from multiple sources using weighted averaging
        
        Args:
            source_features: Dict of {source_name: features_dict}
        
        Returns:
            Combined features dict with all audio features
        """
        if not source_features:
            return cls._default_features()
        
        # If we only have one source, use it directly
        if len(source_features) == 1:
            source, features = list(source_features.items())[0]
            logger.info(f"Using single source: {source}")
            return cls._normalize_features(features)
        
        logger.info(f"Combining features from {len(source_features)} sources: {list(source_features.keys())}")
        
        # Initialize combined features
        combined = {}
        
        # List of features to combine
        feature_names = [
            'acousticness', 'danceability', 'energy', 'instrumentalness',
            'liveness', 'loudness', 'speechiness', 'tempo', 'valence',
            'duration_ms', 'key'
        ]
        
        for feature in feature_names:
            weighted_values = []
            total_weight = 0
            
            for source, features in source_features.items():
                if feature in features and features[feature] is not None:
                    try:
                        # Convert to float (handles strings, ints, floats)
                        value = float(features[feature])
                        weight = cls.SOURCE_WEIGHTS.get(source, 0.5)
                        
                        weighted_values.append(value * weight)
                        total_weight += weight
                    except (ValueError, TypeError):
                        # Skip values that can't be converted to float
                        logger.debug(f"Skipping non-numeric value for {feature} from {source}: {features[feature]}")
                        continue
            
            if weighted_values and total_weight > 0:
                # Weighted average
                combined[feature] = sum(weighted_values) / total_weight
            else:
                # Use default
                combined[feature] = cls._default_features()[feature]
        
        logger.info(f"✅ Combined features from multiple sources successfully")
        return combined
    
    @staticmethod
    def _normalize_features(features: Dict) -> Dict:
        """Ensure all required features exist with sensible defaults"""
        defaults = FeatureFusion._default_features()
        
        for key in defaults:
            if key not in features or features[key] is None:
                features[key] = defaults[key]
        
        return features
    
    @staticmethod
    def _default_features() -> Dict:
        """Return default neutral features"""
        return {
            'acousticness': 0.5,
            'danceability': 0.5,
            'energy': 0.5,
            'instrumentalness': 0.5,
            'liveness': 0.1,
            'loudness': -10.0,
            'speechiness': 0.1,
            'tempo': 120.0,
            'valence': 0.5,
            'duration_ms': 200000,
            'key': 0
        }
    
    @classmethod
    def get_fused_features(
        cls,
        track_name: str,
        artist_name: str,
        preview_url: Optional[str] = None,
        track_id: Optional[str] = None
    ) -> Dict:
        """
        Main method: Get features from all sources and combine them
        
        This is the "smart" feature extraction that tries everything!
        """
        logger.info(f"🔍 Fetching features from multiple sources for: {track_name} by {artist_name}")
        
        # Fetch from all sources in parallel
        source_features = cls.fetch_from_all_sources(
            track_name,
            artist_name,
            preview_url,
            track_id
        )
        
        # Combine with weighted averaging
        combined = cls.combine_features(source_features)
        
        # Add metadata about sources used
        combined['_sources_used'] = list(source_features.keys())
        combined['_num_sources'] = len(source_features)
        
        logger.info(f"✅ Final features using {len(source_features)} sources: {', '.join(source_features.keys())}")
        
        return combined


# Global instance
feature_fusion = FeatureFusion()

