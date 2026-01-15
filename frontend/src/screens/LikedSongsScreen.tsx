import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  Animated,
  RefreshControl,
  Linking,
  Platform,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { getLikedSongs, removeLikedSong } from '../services/api';
import { useNavigation } from '@react-navigation/native';

interface LikedSong {
  id: string;
  name: string;
  artist: string;
  image_url?: string;
  audio_features?: any;
  metadata?: any;
  swiped_at?: string;
}

export const LikedSongsScreen: React.FC = () => {
  const { user } = useAuth();
  const navigation = useNavigation();
  const [songs, setSongs] = useState<LikedSong[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(30)).current;

  useEffect(() => {
    if (user) {
      loadLikedSongs();
    }
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.spring(slideAnim, {
        toValue: 0,
        tension: 50,
        friction: 8,
        useNativeDriver: true,
      }),
    ]).start();
  }, [user]);

  const loadLikedSongs = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const data = await getLikedSongs(user.id);
      console.log('Loaded liked songs:', data.songs?.length || 0);
      setSongs(data.songs || []);
    } catch (error) {
      console.error('Error loading liked songs:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadLikedSongs();
    setRefreshing(false);
  };

  const handleDeleteSong = async (song: LikedSong) => {
    console.log('=== handleDeleteSong CALLED ===');
    console.log('Song:', song.id, song.name);
    console.log('User:', user?.id);
    
    if (!user) {
      console.log('No user, returning');
      return;
    }
    
    const songToDelete = song;
    const currentSongs = songs;
    
    console.log('=== DELETE SONG START ===');
    console.log('Song to delete:', songToDelete.id, songToDelete.name);
    console.log('Current songs count:', currentSongs.length);
    
    // Immediately remove from UI for instant feedback
    setSongs(prevSongs => {
      const beforeCount = prevSongs.length;
      const filtered = prevSongs.filter(s => s.id !== songToDelete.id);
      const afterCount = filtered.length;
      console.log(`✅ UI UPDATE: Before=${beforeCount}, After=${afterCount}`);
      return filtered;
    });
    
    // Then call the API
    try {
      console.log('Calling API...');
      const response = await removeLikedSong(user.id, songToDelete.id);
      console.log('✅ API SUCCESS:', response);
      
      // Reload to ensure consistency
      await loadLikedSongs();
    } catch (error: any) {
      console.error('❌ API ERROR:', error);
      console.error('Error response:', error?.response?.data);
      
      // Reload to restore if failed
      await loadLikedSongs();
      
      Alert.alert('Error', error?.response?.data?.detail || 'Failed to remove song');
    }
  };

  const openInSpotify = async (song: LikedSong) => {
    try {
      // If we have a Spotify track ID, use direct link
      let url: string;
      
      if (song.id && song.id.length === 22) {
        // Looks like a Spotify track ID (22 characters)
        url = Platform.OS === 'web'
          ? `https://open.spotify.com/track/${song.id}`
          : `spotify:track:${song.id}`;
      } else {
        // Fallback to search
        const searchQuery = encodeURIComponent(`${song.name} ${song.artist}`);
        url = Platform.OS === 'web'
          ? `https://open.spotify.com/search/${searchQuery}`
          : `spotify:search:${searchQuery}`;
      }
      
      // For web, always use web URL
      if (Platform.OS === 'web') {
        if (song.id && song.id.length === 22) {
          url = `https://open.spotify.com/track/${song.id}`;
        } else {
          url = `https://open.spotify.com/search/${encodeURIComponent(`${song.name} ${song.artist}`)}`;
        }
      }
      
      const canOpen = Platform.OS === 'web' ? true : await Linking.canOpenURL(url);
      if (canOpen) {
        await Linking.openURL(url);
      } else {
        // Fallback to web search URL
        const fallbackUrl = `https://open.spotify.com/search/${encodeURIComponent(`${song.name} ${song.artist}`)}`;
        await Linking.openURL(fallbackUrl);
      }
    } catch (error) {
      console.error('Error opening Spotify:', error);
      // Fallback to web URL
      try {
        await Linking.openURL(`https://open.spotify.com/search/${encodeURIComponent(`${song.name} ${song.artist}`)}`);
      } catch (e) {
        Alert.alert('Error', 'Could not open Spotify. Please try searching manually.');
      }
    }
  };

  const openInAppleMusic = async (song: LikedSong) => {
    try {
      // Try to get Apple Music track ID from metadata first
      let appleMusicUrl: string;
      
      // Check if we have Apple Music ID in metadata
      const appleMusicId = (song.metadata as any)?.apple_music_id || 
                          (song.metadata as any)?.itunes_id ||
                          (song.metadata as any)?.appleMusicId;
      
      if (appleMusicId) {
        // Direct link to track using Apple Music ID
        appleMusicUrl = `https://music.apple.com/us/album/track/${appleMusicId}`;
      } else {
        // Use iTunes Search API to find the track, then construct direct link
        // First, try to search via iTunes API to get the track ID
        const searchQuery = encodeURIComponent(`${song.name} ${song.artist}`);
        const itunesSearchUrl = `https://itunes.apple.com/search?term=${searchQuery}&media=music&limit=1`;
        
        try {
          const response = await fetch(itunesSearchUrl);
          const data = await response.json();
          
          if (data.results && data.results.length > 0) {
            const track = data.results[0];
            // Construct direct Apple Music link
            // Format: https://music.apple.com/{country}/album/{album-name}/id{collectionId}?i={trackId}
            const trackId = track.trackId;
            const collectionId = track.collectionId;
            const country = 'us'; // Default to US, could be made dynamic
            
            if (trackId && collectionId) {
              appleMusicUrl = `https://music.apple.com/${country}/album/id${collectionId}?i=${trackId}`;
            } else {
              // Fallback to search if we can't construct direct link
              appleMusicUrl = `https://music.apple.com/search?term=${searchQuery}`;
            }
          } else {
            // No results found, use search
            appleMusicUrl = `https://music.apple.com/search?term=${searchQuery}`;
          }
        } catch (fetchError) {
          console.error('Error fetching iTunes data:', fetchError);
          // Fallback to search
          appleMusicUrl = `https://music.apple.com/search?term=${searchQuery}`;
        }
      }
      
      await Linking.openURL(appleMusicUrl);
    } catch (error) {
      console.error('Error opening Apple Music:', error);
      Alert.alert('Error', 'Could not open Apple Music. Please try searching manually.');
    }
  };

  if (!user) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Please log in to view your liked songs</Text>
      </View>
    );
  }

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#667eea" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => (navigation as any).goBack()}
        >
          <Ionicons name="arrow-back" size={24} color="#1a1a1a" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Liked Songs</Text>
        <View style={styles.headerRight} />
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={true}
        bounces={true}
        scrollEnabled={true}
      >
        {songs.length === 0 ? (
          <Animated.View
            style={[
              styles.emptyContainer,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <Ionicons name="heart-outline" size={80} color="#ccc" />
            <Text style={styles.emptyText}>No liked songs yet</Text>
            <Text style={styles.emptySubtext}>Start swiping to like songs!</Text>
          </Animated.View>
        ) : (
          <>
            <Text style={styles.countText}>{songs.length} liked {songs.length === 1 ? 'song' : 'songs'}</Text>
            {songs.map((song, index) => {
              // Debug: log each song being rendered
              if (index === 0) {
                console.log('Rendering songs list. Count:', songs.length, 'First song ID:', song.id);
              }
              return (
              <Animated.View
                key={song.id}
                style={[
                  styles.songCard,
                  {
                    opacity: fadeAnim,
                    transform: [
                      {
                        translateY: slideAnim.interpolate({
                          inputRange: [0, 1],
                          outputRange: [0, index * 10],
                        }),
                      },
                    ],
                  },
                ]}
              >
                <View style={styles.songImageContainer}>
                  <Image
                    source={{ 
                      uri: song.image_url || 
                            song.metadata?.image_url || 
                            (song.metadata as any)?.album?.images?.[0]?.url ||
                            'https://via.placeholder.com/80' 
                    }}
                    style={styles.songImage}
                    onError={(e) => {
                      console.log('Image load error for song:', song.name, 'image_url:', song.image_url, 'metadata:', song.metadata);
                    }}
                  />
                </View>
                <View style={styles.songInfo}>
                  <Text style={styles.songName} numberOfLines={1}>{song.name}</Text>
                  <Text style={styles.songArtist} numberOfLines={1}>{song.artist}</Text>
                  {song.swiped_at && (
                    <Text style={styles.songDate}>
                      Liked {new Date(song.swiped_at).toLocaleDateString()}
                    </Text>
                  )}
                </View>
                <View style={styles.actionButtons}>
                  <TouchableOpacity
                    style={styles.musicButton}
                    onPress={() => openInSpotify(song)}
                    activeOpacity={0.7}
                  >
                    <Image
                      source={{ uri: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/1024px-Spotify_logo_without_text.svg.png' }}
                      style={styles.spotifyLogoImage}
                      onError={() => {
                        // Fallback to text if image fails to load
                        console.log('Spotify logo image failed to load');
                      }}
                    />
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.musicButton, styles.appleMusicButton]}
                    onPress={() => openInAppleMusic(song)}
                    activeOpacity={0.7}
                  >
                    <Ionicons name="logo-apple" size={18} color="white" />
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={styles.deleteButton}
                    onPress={() => {
                      console.log('🗑️ DELETE BUTTON PRESSED!');
                      console.log('Song ID:', song.id);
                      console.log('Song Name:', song.name);
                      handleDeleteSong(song);
                    }}
                    activeOpacity={0.7}
                    hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                  >
                    <Ionicons name="trash-outline" size={20} color="white" />
                  </TouchableOpacity>
                </View>
              </Animated.View>
              );
            })}
          </>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    paddingTop: 60,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#1a1a1a',
    flex: 1,
    textAlign: 'center',
  },
  headerRight: {
    width: 40,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40, // Extra padding at bottom so last item is fully visible
    flexGrow: 1,
  },
  countText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
    fontWeight: '600',
  },
  songCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 15,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  songImageContainer: {
    width: 60,
    height: 60,
    borderRadius: 10,
    overflow: 'hidden',
    marginRight: 15,
    backgroundColor: '#f0f0f0',
  },
  songImage: {
    width: '100%',
    height: '100%',
  },
  songInfo: {
    flex: 1,
  },
  songName: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  songArtist: {
    fontSize: 15,
    color: '#666',
    marginBottom: 4,
    fontWeight: '500',
  },
  songDate: {
    fontSize: 12,
    color: '#999',
  },
  actionButtons: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  musicButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#1DB954', // Spotify green
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#1DB954',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  appleMusicButton: {
    backgroundColor: '#FA243C', // Apple Music red
    shadowColor: '#FA243C',
  },
  deleteButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#F44336', // Red for delete
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#F44336',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  spotifyLogoImage: {
    width: 18,
    height: 18,
    tintColor: 'white',
    resizeMode: 'contain',
  },
  heartIcon: {
    marginLeft: 4,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 100,
  },
  emptyText: {
    fontSize: 24,
    fontWeight: '800',
    color: '#666',
    marginTop: 20,
    marginBottom: 10,
  },
  emptySubtext: {
    fontSize: 16,
    color: '#999',
  },
  errorText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginTop: 100,
  },
});

