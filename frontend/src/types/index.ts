export interface Song {
  id: string;
  name: string;
  artist: string;
  album: string;
  preview_url?: string;
  image_url: string;
  popularity: number;
  similarity_score: number; // Changed from match_score to similarity_score
  audio_features: {
    danceability: number;
    energy: number;
    valence: number;
    tempo: number;
    acousticness: number;
    instrumentalness: number;
    liveness: number;
    speechiness: number;
  };
  metadata: { // Changed from track_metadata to metadata
    genres: string[];
    lastfm_tags: string[];
    enhanced_tags: string[];
    release_year: number;
    popularity: number;
    lastfm_similarity: number;
  };
}

export interface SwipeData {
  song_id: string;
  song_name: string;
  artist_name: string;
  direction: 'left' | 'right';
  audio_features: any;
  metadata: any; // Changed from track_metadata to metadata
}

export interface User {
  id: number;
  username: string;
  email: string;
}