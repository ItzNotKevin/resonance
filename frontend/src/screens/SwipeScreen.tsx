import React, { useState, useEffect, useCallback, useRef } from 'react';
import { View, Text, StyleSheet, Alert, ActivityIndicator, TextInput, TouchableOpacity, TouchableWithoutFeedback, Image, Animated, Dimensions } from 'react-native';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import Swiper from 'react-native-deck-swiper';
import { SwipeCard, stopAllAudio } from '../components/SwipeCard';
import { searchSongs, getRecommendations, recordSwipe } from '../services/api';
import { Song, SwipeData } from '../types';
import { useAuth } from '../context/AuthContext';
import { useNavigation } from '@react-navigation/native';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

export const SwipeScreen: React.FC = () => {
  const { user } = useAuth();
  const navigation = useNavigation();
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Song[]>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [cardIndex, setCardIndex] = useState(0);
  const swiperRef = useRef<any>(null);
  
  // Animation values
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;
  const searchResultsOpacity = useRef(new Animated.Value(0)).current;
  const searchResultsScale = useRef(new Animated.Value(0.95)).current;
  const titleScale = useRef(new Animated.Value(1)).current;
  const backgroundAnim = useRef(new Animated.Value(0)).current;

  const loadRecommendations = async (seedId: string) => {
    setLoading(true);
    try {
      const response = await getRecommendations(seedId, user?.id || null);
      console.log('Recommendations response:', response);
      // The API returns the recommendations directly, not wrapped in a 'recommendations' property
      if (response && Array.isArray(response) && response.length > 0) {
        setSongs(response);
      } else {
        console.warn('No recommendations returned or empty array');
        Alert.alert('No Recommendations', 'Could not find similar songs. Please try a different search.');
        setSongs([]); // Explicitly set to empty to show home screen
      }
    } catch (error: any) {
      console.error('Error loading recommendations:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Unknown error occurred';
      console.error('Error details:', errorMessage);
      Alert.alert('Error', `Failed to load recommendations: ${errorMessage}`);
      setSongs([]); // Explicitly set to empty to show home screen
    } finally {
      setLoading(false);
    }
  };

  const handleSwipe = async (direction: 'left' | 'right', song: Song, cardIndex: number) => {
    try {
      // Ensure image_url is included in metadata
      const metadataWithImage = {
        ...song.metadata,
        image_url: song.image_url, // Add image_url to metadata for storage
      };
      
      const swipeData = {
        song_id: song.id,
        song_name: song.name,
        artist_name: song.artist,
        direction,
        audio_features: song.audio_features,
        track_metadata: metadataWithImage, // Backend expects track_metadata with image_url
        user_id: user?.id || null,
      };
      
      const response = await recordSwipe(swipeData);
      console.log(`Swiped ${direction} on ${song.name}`);
      
      // Check if preferences were updated (every 10 swipes)
      if (response?.preferences_updated) {
        console.log('✅ Preferences updated! Recommendations will improve.');
        // Could show a toast notification here
      }
      
      // Fetch new recommendations when running low on cards (5 or fewer remaining)
      const remainingCards = songs.length - cardIndex - 1;
      if (remainingCards <= 5 && songs.length > 0) {
        console.log(`🔄 Running low on cards (${remainingCards} remaining), fetching more recommendations...`);
        // Use the first song as seed to get more recommendations
        // This ensures continuity with the initial search
        const seedId = songs[0].id;
        try {
          const newRecommendations = await getRecommendations(seedId, user?.id || null);
          if (newRecommendations && newRecommendations.length > 0) {
            // Filter out songs already shown
            const existingIds = new Set(songs.map((s: Song) => s.id));
            const freshSongs = newRecommendations.filter((s: Song) => !existingIds.has(s.id));
            if (freshSongs.length > 0) {
              setSongs(prevSongs => [...prevSongs, ...freshSongs]);
              console.log(`✅ Added ${freshSongs.length} new recommendations`);
            } else {
              console.log('⚠️ No new unique recommendations found');
            }
          }
        } catch (error) {
          console.error('Error fetching more recommendations:', error);
        }
      }
    } catch (error) {
      console.error('Error recording swipe:', error);
    }
  };

  const searchAndLoad = async (query: string) => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const searchResults = await searchSongs(query);
      console.log('Search results:', searchResults);
      
      // The API returns an array directly, not wrapped in 'tracks'
      if (Array.isArray(searchResults) && searchResults.length > 0) {
        const firstTrack = searchResults[0];
        console.log('Loading recommendations for:', firstTrack);
        await loadRecommendations(firstTrack.id);
        setSearchQuery(''); // Clear search input after loading recommendations
      } else {
        Alert.alert('No Results', 'No songs found for your search');
      }
    } catch (error) {
      console.error('Search error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      Alert.alert('Error', 'Search failed: ' + errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Stop audio when returning to home/search screen
  useEffect(() => {
    if (songs.length === 0) {
      stopAllAudio();
    }
  }, [songs.length]);

  // Animate on mount
  useEffect(() => {
    if (songs.length === 0) {
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
        Animated.loop(
          Animated.sequence([
            Animated.timing(titleScale, {
              toValue: 1.05,
              duration: 2000,
              useNativeDriver: true,
            }),
            Animated.timing(titleScale, {
              toValue: 1,
              duration: 2000,
              useNativeDriver: true,
            }),
          ])
        ),
        Animated.loop(
          Animated.sequence([
            Animated.timing(backgroundAnim, {
              toValue: 1,
              duration: 3000,
              useNativeDriver: false,
            }),
            Animated.timing(backgroundAnim, {
              toValue: 0,
              duration: 3000,
              useNativeDriver: false,
            }),
          ])
        ),
      ]).start();
    }
  }, []);

  // Animate search results
  useEffect(() => {
    if (showSearchResults && searchResults.length > 0) {
      Animated.parallel([
        Animated.timing(searchResultsOpacity, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
        Animated.spring(searchResultsScale, {
          toValue: 1,
          tension: 50,
          friction: 7,
          useNativeDriver: true,
        }),
      ]).start();
    } else {
      Animated.parallel([
        Animated.timing(searchResultsOpacity, {
          toValue: 0,
          duration: 150,
          useNativeDriver: true,
        }),
        Animated.timing(searchResultsScale, {
          toValue: 0.95,
          duration: 150,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [showSearchResults, searchResults.length]);

  // No auto-search on load - user must search manually

  // Real-time search with debouncing
  const performSearch = useCallback(async (query: string) => {
    if (query.trim().length < 2) {
      setSearchResults([]);
      setShowSearchResults(false);
      return;
    }

    try {
      console.log('Performing search for:', query);
      const results = await searchSongs(query);
      console.log('Search results received:', results?.length, 'items');
      setSearchResults(results || []);
      if (results && results.length > 0) {
        setShowSearchResults(true);
        // Force animation to show
        Animated.parallel([
          Animated.timing(searchResultsOpacity, {
            toValue: 1,
            duration: 200,
            useNativeDriver: true,
          }),
          Animated.spring(searchResultsScale, {
            toValue: 1,
            tension: 50,
            friction: 7,
            useNativeDriver: true,
          }),
        ]).start();
      } else {
        setShowSearchResults(false);
      }
    } catch (error: any) {
      console.error('Search error:', error);
      setSearchResults([]);
      setShowSearchResults(false);
      // Show user-friendly error message
      if (error?.response?.status === 503) {
        Alert.alert(
          'Search Unavailable',
          'Spotify API credentials are not configured. Please check your backend configuration.'
        );
      } else if (error?.code === 'ECONNABORTED' || error?.message?.includes('timeout')) {
        Alert.alert(
          'Search Timeout',
          'The search request took too long. Please check if the backend is running and try again.'
        );
      } else if (error?.code === 'ECONNREFUSED') {
        Alert.alert(
          'Connection Error',
          'Cannot connect to backend server. Please make sure the backend is running on port 8000.'
        );
      }
    }
  }, [searchResultsOpacity, searchResultsScale]);

  // Debounced search with faster response - 100ms delay
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      performSearch(searchQuery);
    }, 100); // Faster response while still preventing excessive API calls

    return () => clearTimeout(timeoutId);
  }, [searchQuery, performSearch]);

  // Keyboard controls for swiping
  useEffect(() => {
    if (songs.length === 0 || !swiperRef.current) return;

    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'ArrowLeft' || event.key === 'a' || event.key === 'A') {
        event.preventDefault();
        swiperRef.current?.swipeLeft();
      } else if (event.key === 'ArrowRight' || event.key === 'd' || event.key === 'D') {
        event.preventDefault();
        swiperRef.current?.swipeRight();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [songs.length]);

  const handleSearch = () => {
    if (searchQuery.trim()) {
      searchAndLoad(searchQuery);
      setShowSearchResults(false);
    }
  };

  const handleSearchResultSelect = (song: Song) => {
    setShowSearchResults(false); // Hide immediately when song is selected
    setSearchQuery(''); // Clear the search input
    // Load recommendations directly with the selected song's ID
    setLoading(true);
    loadRecommendations(song.id).catch(error => {
      console.error('Error loading recommendations:', error);
      Alert.alert('Error', 'Failed to load recommendations');
    }).finally(() => {
      setLoading(false);
    });
  };

  // Background opacity for gradient effect
  const bgOpacity = backgroundAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0.5, 1],
  });

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Animated.View 
          style={[
            StyleSheet.absoluteFill,
            {
              backgroundColor: '#667eea',
              opacity: bgOpacity,
            },
          ]} 
        />
        <Animated.View 
          style={[
            StyleSheet.absoluteFill,
            {
              backgroundColor: '#764ba2',
              opacity: backgroundAnim.interpolate({
                inputRange: [0, 1],
                outputRange: [1, 0.5],
              }),
            },
          ]} 
        />
        <ActivityIndicator size="large" color="white" />
        <Animated.Text 
          style={[
            styles.loadingText,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          Loading recommendations...
        </Animated.Text>
      </View>
    );
  }

  // If we have songs, show full-screen swiper
  if (songs.length > 0) {
    return (
      <View style={styles.fullScreenContainer}>
        <View style={styles.topButtons}>
          <TouchableOpacity 
            style={styles.newSearchButton} 
            onPress={() => {
              // Stop all audio playback
              stopAllAudio();
              // Reset to home/search screen
              setSongs([]);
              setSearchQuery('');
              setSearchResults([]);
              setShowSearchResults(false);
              setCardIndex(0);
            }}
          >
            <Ionicons name="home" size={18} color="white" style={{ marginRight: 8 }} />
            <Text style={styles.newSearchButtonText}>Home</Text>
          </TouchableOpacity>
          {user && (
            <>
              <TouchableOpacity 
                style={styles.likedSongsButton} 
                onPress={() => (navigation as any).navigate('LikedSongs')}
              >
                <Ionicons name="heart" size={18} color="white" />
              </TouchableOpacity>
              <TouchableOpacity 
                style={styles.accountButton} 
                onPress={() => (navigation as any).navigate('Account')}
              >
                <Ionicons name="person" size={18} color="white" />
              </TouchableOpacity>
            </>
          )}
        </View>
        <Swiper
          ref={swiperRef}
          cards={songs}
          renderCard={(song, index) => (
            <SwipeCard 
              song={song}
              isTopCard={index === cardIndex}
              onSwipe={(direction) => {
                if (direction === 'left') {
                  swiperRef.current?.swipeLeft();
                } else {
                  swiperRef.current?.swipeRight();
                }
              }} 
            />
          )}
          onSwipedLeft={(index) => {
            console.log('Swiped left on card', index);
            if (songs[index]) {
              handleSwipe('left', songs[index], index);
            }
            setCardIndex(index + 1);
          }}
          onSwipedRight={(index) => {
            console.log('Swiped right on card', index);
            if (songs[index]) {
              handleSwipe('right', songs[index], index);
            }
            setCardIndex(index + 1);
          }}
          cardIndex={cardIndex}
          backgroundColor="transparent"
          stackSize={3}
          stackSeparation={15}
          animateOverlayLabelsOpacity
          animateCardOpacity={false}
          swipeBackCard
          infinite={false}
        />
      </View>
    );
  }

  // Otherwise, show search interface
  return (
    <View style={styles.container}>
        {/* Navigation buttons - always visible when logged in */}
        {user ? (
          <View style={[styles.topButtons, styles.topButtonsSearch]}>
            <TouchableOpacity 
              style={styles.likedSongsButton} 
              onPress={() => {
                console.log('Navigating to LikedSongs, user:', user);
                (navigation as any).navigate('LikedSongs');
              }}
            >
              <Ionicons name="heart" size={18} color="white" />
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.accountButton} 
              onPress={() => {
                console.log('Navigating to Account, user:', user);
                (navigation as any).navigate('Account');
              }}
            >
              <Ionicons name="person" size={18} color="white" />
            </TouchableOpacity>
          </View>
        ) : (
          <View style={[styles.topButtons, styles.topButtonsSearch]}>
            <Text style={{ color: 'white', fontSize: 12, backgroundColor: 'rgba(0,0,0,0.5)', padding: 5, borderRadius: 5 }}>
              Not logged in
            </Text>
          </View>
        )}
        
        {/* Animated gradient background */}
        <Animated.View 
          style={[
            StyleSheet.absoluteFill,
            {
              backgroundColor: '#667eea',
              opacity: bgOpacity,
            },
          ]} 
        />
        <Animated.View 
          style={[
            StyleSheet.absoluteFill,
            {
              backgroundColor: '#764ba2',
              opacity: backgroundAnim.interpolate({
                inputRange: [0, 1],
                outputRange: [1, 0.5],
              }),
            },
          ]} 
        />
        <Animated.View
          style={{
            transform: [{ scale: titleScale }],
          }}
        >
          <Animated.Text 
            style={[
              styles.title,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            Music Discovery
          </Animated.Text>
          <Animated.Text 
            style={[
              styles.subtitle,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            Swipe to discover new music!
          </Animated.Text>
        </Animated.View>
        
        {/* Search Input */}
        <Animated.View 
          style={[
            styles.searchContainer,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          <TextInput
            style={styles.searchInput}
            placeholder="Search for any song or artist..."
            placeholderTextColor="#999"
            value={searchQuery}
            onChangeText={setSearchQuery}
            onSubmitEditing={handleSearch}
            onFocus={() => setShowSearchResults(true)}
          />
          <TouchableOpacity 
            style={styles.searchButton} 
            onPress={handleSearch}
            activeOpacity={0.8}
          >
            <Ionicons name="search" size={24} color="white" />
          </TouchableOpacity>
        </Animated.View>

        {/* Search Results Dropdown */}
        {showSearchResults && searchResults.length > 0 && (
          <Animated.View 
            style={[
              styles.searchResultsContainer,
              {
                opacity: searchResultsOpacity,
                transform: [{ scale: searchResultsScale }],
              },
            ]}
          >
            {searchResults.slice(0, 5).map((song, index) => (
              <TouchableOpacity
                key={`${song.id}-${index}`}
                style={[
                  styles.searchResultItem,
                  index === searchResults.slice(0, 5).length - 1 && styles.lastSearchResultItem
                ]}
                onPress={() => {
                  console.log('Search result clicked:', song.name);
                  handleSearchResultSelect(song);
                }}
                activeOpacity={0.7}
              >
                <View style={styles.searchResultContent}>
                  {song.image_url && (
                    <Image 
                      source={{ uri: song.image_url }} 
                      style={styles.searchResultImage}
                      onError={() => console.log('Album cover failed to load')}
                    />
                  )}
                  <View style={styles.searchResultText}>
                    <Text style={styles.searchResultTitle} numberOfLines={1}>{song.name}</Text>
                    <Text style={styles.searchResultArtist} numberOfLines={1}>{song.artist}</Text>
                    {song.album && (
                      <Text style={styles.searchResultAlbum} numberOfLines={1}>{song.album}</Text>
                    )}
                  </View>
                </View>
              </TouchableOpacity>
            ))}
          </Animated.View>
        )}
        
        {/* Backdrop to close search results when clicking outside */}
        {showSearchResults && searchResults.length > 0 && (
          <TouchableWithoutFeedback onPress={() => setShowSearchResults(false)}>
            <View style={styles.searchResultsBackdrop} />
          </TouchableWithoutFeedback>
        )}
        
        {/* Debug: Show search state */}
        {__DEV__ && (
          <View style={{ position: 'absolute', bottom: 20, left: 20, backgroundColor: 'rgba(0,0,0,0.7)', padding: 10, borderRadius: 5, zIndex: 2000 }}>
            <Text style={{ color: 'white', fontSize: 10 }}>
              Results: {searchResults.length} | Show: {showSearchResults ? 'yes' : 'no'}
            </Text>
          </View>
        )}
      
        {!loading && (
          <Animated.View 
            style={[
              styles.emptyContainer,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <Ionicons name="musical-notes" size={64} color="rgba(255, 255, 255, 0.5)" />
            <Text style={styles.emptyText}>No recommendations yet</Text>
            <Text style={styles.emptySubtext}>Search for a song to get started!</Text>
          </Animated.View>
        )}
      </View>
  );
};

const styles = StyleSheet.create({
  fullScreenContainer: {
    flex: 1,
    backgroundColor: '#000',
  },
  topButtons: {
    position: 'absolute',
    top: 60,
    right: 20,
    flexDirection: 'row',
    gap: 12,
    zIndex: 1000,
  },
  topButtonsSearch: {
    top: 20,
  },
  newSearchButton: {
    backgroundColor: '#2196F3',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 25,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#2196F3',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 8,
  },
  likedSongsButton: {
    backgroundColor: '#4CAF50',
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#4CAF50',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 8,
  },
  accountButton: {
    backgroundColor: '#667eea',
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#667eea',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 8,
  },
  newSearchButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  container: {
    flex: 1,
    paddingTop: 60,
    paddingHorizontal: 20,
    position: 'relative',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 20,
    fontSize: 18,
    color: 'white',
    fontWeight: '600',
  },
  title: {
    fontSize: 42,
    fontWeight: '900',
    textAlign: 'center',
    marginBottom: 12,
    color: 'white',
    letterSpacing: -1,
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  subtitle: {
    fontSize: 20,
    textAlign: 'center',
    marginBottom: 40,
    color: 'rgba(255, 255, 255, 0.9)',
    fontWeight: '500',
  },
  searchContainer: {
    flexDirection: 'row',
    marginBottom: 20,
    alignItems: 'center',
  },
  searchInput: {
    flex: 1,
    height: 56,
    borderWidth: 0,
    borderRadius: 28,
    paddingHorizontal: 24,
    fontSize: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    marginRight: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 6,
    fontWeight: '500',
  },
  searchButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 6,
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.5)',
  },
  searchButtonText: {
    fontSize: 20,
    color: 'white',
  },
  searchResultsBackdrop: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 999,
  },
  searchResultsContainer: {
    position: 'absolute',
    top: 280,
    left: 20,
    right: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.98)',
    borderRadius: 20,
    maxHeight: 400,
    overflow: 'hidden',
    zIndex: 1000,
    elevation: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
  },
  searchResultItem: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  lastSearchResultItem: {
    borderBottomWidth: 0,
  },
  searchResultContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  searchResultImage: {
    width: 60,
    height: 60,
    borderRadius: 12,
    marginRight: 16,
    backgroundColor: '#f0f0f0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  searchResultText: {
    flex: 1,
  },
  searchResultTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  searchResultArtist: {
    fontSize: 15,
    color: '#555',
    marginBottom: 2,
    fontWeight: '500',
  },
  searchResultAlbum: {
    fontSize: 13,
    color: '#888',
    fontWeight: '400',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingBottom: 100,
  },
  emptyText: {
    fontSize: 26,
    fontWeight: '800',
    color: 'rgba(255, 255, 255, 0.9)',
    marginTop: 20,
    marginBottom: 8,
    textShadowColor: 'rgba(0, 0, 0, 0.2)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  emptySubtext: {
    fontSize: 18,
    color: 'rgba(255, 255, 255, 0.7)',
    fontWeight: '500',
  },
});