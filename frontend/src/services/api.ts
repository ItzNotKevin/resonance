import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 seconds for search, longer for recommendations
});

// Separate instance for recommendations with longer timeout
export const recommendationsApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for recommendations
});

export const searchSongs = async (query: string) => {
  try {
    console.log(`Searching for: "${query}"`);
    const response = await api.get(`/api/search?query=${encodeURIComponent(query)}`);
    console.log(`Search successful, found ${response.data.length} results`);
    return response.data;
  } catch (error: any) {
    console.error('Search error:', error);
    if (error?.code === 'ECONNREFUSED') {
      throw new Error('Backend server is not running. Please start it with: cd backend && python main.py');
    }
    throw error;
  }
};

export const getRecommendations = async (seedId: string, userId: number | null = null) => {
  try {
    const response = await recommendationsApi.post('/api/recommendations/fast', {
      seed_id: seedId,
      user_id: userId
    });
    return response.data;
  } catch (error: any) {
    console.error('Recommendations error:', error);
    throw error;
  }
};

export const recordSwipe = async (swipeData: any) => {
  try {
    const response = await api.post('/api/swipe', swipeData);
    return response.data;
  } catch (error: any) {
    console.error('Swipe error:', error);
    throw error;
  }
};

export const login = async (username: string, password: string) => {
  try {
    const response = await api.post('/api/auth/login', {
      username,
      password
    });
    return response.data;
  } catch (error: any) {
    console.error('Login error:', error);
    throw error;
  }
};

export const register = async (username: string, password: string) => {
  try {
    const response = await api.post('/api/auth/register', {
      username,
      password
    });
    return response.data;
  } catch (error: any) {
    console.error('Register error:', error);
    throw error;
  }
};

export const getUserPreferences = async (userId: number) => {
  try {
    const response = await api.get(`/api/user/preferences/${userId}`);
    return response.data;
  } catch (error: any) {
    console.error('Get preferences error:', error);
    throw error;
  }
};

export const getLikedSongs = async (userId: number) => {
  try {
    const response = await api.get(`/api/user/liked-songs/${userId}`);
    return response.data;
  } catch (error: any) {
    console.error('Get liked songs error:', error);
    throw error;
  }
};

export const removeLikedSong = async (userId: number, songId: string) => {
  try {
    console.log(`Removing liked song: userId=${userId}, songId=${songId}`);
    const response = await api.delete(`/api/user/liked-songs/${userId}/${encodeURIComponent(songId)}`);
    console.log('Remove liked song response:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('Remove liked song error:', error);
    console.error('Error details:', error?.response?.data);
    throw error;
  }
};