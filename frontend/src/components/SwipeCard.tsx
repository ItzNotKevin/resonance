import React, { useState, useEffect, useRef } from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity, Platform, Animated, Dimensions } from 'react-native';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import { Song } from '../types';

// Global audio manager to track currently playing audio
let currentlyPlayingAudio: HTMLAudioElement | null = null;

// Export function to stop all audio playback
export const stopAllAudio = () => {
  if (currentlyPlayingAudio) {
    currentlyPlayingAudio.pause();
    currentlyPlayingAudio.currentTime = 0;
    currentlyPlayingAudio = null;
    console.log('Stopped all audio playback');
  }
};

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface SwipeCardProps {
  song: Song;
  isTopCard: boolean;
  onSwipe: (direction: 'left' | 'right') => void;
}

// Helper function to extract dominant color from image (web only)
const extractDominantColor = (imageUrl: string): Promise<string> => {
  return new Promise((resolve) => {
    if (Platform.OS !== 'web') {
      resolve('#667eea'); // Default color for mobile
      return;
    }

    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas');
        canvas.width = 50;
        canvas.height = 50;
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          resolve('#667eea');
          return;
        }
        ctx.drawImage(img, 0, 0, 50, 50);
        
        // Sample pixels and get average color
        const imageData = ctx.getImageData(0, 0, 50, 50);
        const data = imageData.data;
        let r = 0, g = 0, b = 0, count = 0;
        
        // Sample every 4th pixel for performance
        for (let i = 0; i < data.length; i += 16) {
          r += data[i];
          g += data[i + 1];
          b += data[i + 2];
          count++;
        }
        
        r = Math.floor(r / count);
        g = Math.floor(g / count);
        b = Math.floor(b / count);
        
        // Convert to hex
        const hex = `#${[r, g, b].map(x => {
          const hex = x.toString(16);
          return hex.length === 1 ? '0' + hex : hex;
        }).join('')}`;
        
        resolve(hex);
      } catch (e) {
        resolve('#667eea');
      }
    };
    img.onerror = () => resolve('#667eea');
    img.src = imageUrl;
  });
};

// Helper to get lighter/darker variations
const lightenColor = (hex: string, percent: number): string => {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = (num >> 16) & 0xFF;
  const g = (num >> 8) & 0xFF;
  const b = num & 0xFF;
  
  // If percent is negative, darken; if positive, lighten
  const factor = percent > 0 ? percent : -percent;
  const adjust = Math.floor(255 * factor);
  
  const newR = Math.max(0, Math.min(255, percent > 0 ? r + adjust : r - adjust));
  const newG = Math.max(0, Math.min(255, percent > 0 ? g + adjust : g - adjust));
  const newB = Math.max(0, Math.min(255, percent > 0 ? b + adjust : b - adjust));
  
  return `#${[newR, newG, newB].map(x => {
    const hex = x.toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  }).join('')}`;
};

export const SwipeCard: React.FC<SwipeCardProps> = ({ song, isTopCard, onSwipe }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(30);
  const [dominantColor, setDominantColor] = useState('#667eea');
  const [lightColor, setLightColor] = useState('#f0f0f0');
  const [darkColor, setDarkColor] = useState('#1a1a1a');
  
  // Animation values
  const pulseValue = useRef(new Animated.Value(1)).current;
  const cardScale = useRef(new Animated.Value(isTopCard ? 1 : 0.95)).current;
  const cardOpacity = useRef(new Animated.Value(1)).current; // Always start at 1
  const progressWidth = useRef(new Animated.Value(0)).current;
  const glowValue = useRef(new Animated.Value(0)).current;
  const imageScale = useRef(new Animated.Value(1)).current;

  // Extract colors from album cover
  useEffect(() => {
    if (song.image_url) {
      extractDominantColor(song.image_url).then((color) => {
        setDominantColor(color);
        setLightColor(lightenColor(color, 0.85));
        setDarkColor(lightenColor(color, -0.3));
      });
    }
  }, [song.image_url]);
  
  // Start animations when card becomes top card
  useEffect(() => {
    if (isTopCard) {
      // Card entrance animation
      Animated.parallel([
        Animated.spring(cardScale, {
          toValue: 1,
          tension: 50,
          friction: 7,
          useNativeDriver: true,
        }),
        Animated.timing(cardOpacity, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.spring(imageScale, {
          toValue: 1.05,
          tension: 40,
          friction: 6,
          useNativeDriver: true,
        }),
      ]).start();
      
      // Subtle pulse animation for the whole card
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseValue, {
            toValue: 1.01,
            duration: 4000,
            useNativeDriver: true,
          }),
          Animated.timing(pulseValue, {
            toValue: 1,
            duration: 4000,
            useNativeDriver: true,
          }),
        ])
      ).start();

      // Subtle image breathing effect
      Animated.loop(
        Animated.sequence([
          Animated.timing(imageScale, {
            toValue: 1.03,
            duration: 3000,
            useNativeDriver: true,
          }),
          Animated.timing(imageScale, {
            toValue: 1.05,
            duration: 3000,
            useNativeDriver: true,
          }),
        ])
      ).start();

      // Glow effect
      Animated.loop(
        Animated.sequence([
          Animated.timing(glowValue, {
            toValue: 1,
            duration: 2500,
            useNativeDriver: true,
          }),
          Animated.timing(glowValue, {
            toValue: 0.5,
            duration: 2500,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      // Card behind - just scale down slightly, keep fully opaque
      Animated.parallel([
        Animated.timing(cardScale, {
          toValue: 0.95,
          duration: 200,
          useNativeDriver: true,
        }),
        Animated.timing(imageScale, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();
      // Keep opacity at 1 for all cards
      cardOpacity.setValue(1);
    }
  }, [isTopCard]);
  
  // Update progress bar animation
  useEffect(() => {
    if (isTopCard && duration > 0) {
      Animated.timing(progressWidth, {
        toValue: (currentTime / duration) * 100,
        duration: 100,
        useNativeDriver: false,
      }).start();
    }
  }, [currentTime, duration, isTopCard]);
  
  // Glow opacity
  const glowOpacity = glowValue.interpolate({
    inputRange: [0, 1],
    outputRange: [0.2, 0.5],
  });

  // Auto-play when component mounts AND it's the top card
  useEffect(() => {
    const initAudio = async () => {
      // Always stop previously playing audio when a new card becomes top
      if (isTopCard) {
        if (currentlyPlayingAudio) {
          currentlyPlayingAudio.pause();
          currentlyPlayingAudio.currentTime = 0;
          currentlyPlayingAudio = null;
          console.log('Stopped previously playing audio');
        }
        // Also stop local audio if it exists
        if (audio) {
          audio.pause();
          audio.currentTime = 0;
          setIsPlaying(false);
        }
      }
      
      if (isTopCard && song.preview_url && Platform.OS === 'web') {
        try {
          // Create new audio instance
          const newAudio = new Audio(song.preview_url);
          
          // Set up event listeners
          newAudio.onloadedmetadata = () => {
            setDuration(newAudio.duration);
          };
          
          newAudio.ontimeupdate = () => {
            setCurrentTime(newAudio.currentTime);
          };
          
          newAudio.onended = () => {
            console.log('Audio playback ended');
            setIsPlaying(false);
            setCurrentTime(0);
          };
          
          newAudio.onerror = (e) => {
            console.error('Audio playback error:', e);
            setIsPlaying(false);
          };
          
          // Store in global variable and local state
          currentlyPlayingAudio = newAudio;
          setAudio(newAudio);
          
          // Play audio
          await newAudio.play();
          setIsPlaying(true);
          console.log('Auto-playing audio preview:', song.name);
        } catch (error) {
          console.error('Error auto-playing audio:', error);
          setIsPlaying(false);
        }
      } else if (!isTopCard && audio) {
        // Stop audio when card is no longer on top
        console.log('Stopping audio for non-top card:', song.name);
        audio.pause();
        audio.currentTime = 0;
        setIsPlaying(false);
        
        // Clear global reference if this was the currently playing audio
        if (currentlyPlayingAudio === audio) {
          currentlyPlayingAudio = null;
        }
      }
    };

    initAudio();
    
    // Cleanup: stop audio when component unmounts
    return () => {
      if (audio) {
        audio.pause();
        audio.currentTime = 0;
      }
    };
  }, [isTopCard, song.preview_url, song.id]); // Re-run if top card changes, preview URL changes, or song changes

  const playPreview = () => {
    if (audio) {
      audio.play().then(() => {
        setIsPlaying(true);
        console.log('Resumed audio playback');
      }).catch(error => {
        console.error('Error resuming audio:', error);
      });
    }
  };

  const stopPreview = () => {
    if (audio) {
      audio.pause();
      setIsPlaying(false);
      console.log('Paused audio playback');
    }
  };

  const skipBackward = () => {
    if (audio) {
      audio.currentTime = Math.max(0, audio.currentTime - 5);
    }
  };

  const skipForward = () => {
    if (audio) {
      audio.currentTime = Math.min(audio.duration, audio.currentTime + 5);
    }
  };


  // Calculate match color based on score (use album colors with match indicator)
  const matchColor = song.similarity_score > 0.7 ? '#4CAF50' : song.similarity_score > 0.5 ? '#FF9800' : '#F44336';
  
  // Create glow color from dominant color
  const cardGlowColor = `${dominantColor}80`; // Add transparency

  return (
    <Animated.View 
      style={[
        styles.card,
        {
          transform: [{ scale: Animated.multiply(cardScale, pulseValue) }],
          opacity: cardOpacity,
          backgroundColor: lightColor,
        },
      ]}
    >
      {/* Themed gradient overlay background */}
      <Animated.View 
        style={[
          styles.gradientOverlay,
          {
            opacity: glowOpacity,
            backgroundColor: cardGlowColor,
          },
        ]} 
      />
      
      <Animated.View
        style={[
          styles.imageContainer,
          {
            transform: [{ scale: imageScale }],
          },
        ]}
      >
        <Image source={{ uri: song.image_url }} style={styles.image} />
        {/* Gradient overlay on image with theme color */}
        <View style={[styles.imageGradient, { 
          backgroundColor: Platform.OS === 'web' ? 'transparent' : 'transparent',
        }]} />
        {Platform.OS === 'web' && (
          <View style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: '50%',
            background: `linear-gradient(to top, ${dominantColor}CC 0%, transparent 100%)`,
          }} />
        )}
      </Animated.View>
      <View style={styles.content}>
        <View style={styles.titleContainer}>
          <Text style={[styles.title, { color: darkColor }]} numberOfLines={2}>{song.name}</Text>
          <Animated.View 
            style={[
              styles.titleUnderline,
              { backgroundColor: dominantColor, opacity: glowOpacity },
            ]} 
          />
        </View>
        <Text style={[styles.artist, { color: darkColor }]}>{song.artist}</Text>
        <Text style={[styles.album, { color: lightenColor(dominantColor, -0.2) }]}>{song.album}</Text>
        
        <View style={styles.stats}>
          <View style={[styles.statBadge, { backgroundColor: `${matchColor}25` }]}>
            <View style={[styles.statDot, { backgroundColor: matchColor }]} />
            <Text style={[styles.matchScore, { color: matchColor }]}>
              {Math.round(song.similarity_score * 100)}% Match
            </Text>
          </View>
          {(song.popularity !== undefined && song.popularity !== null) || (song.metadata?.popularity !== undefined) ? (
            <View style={[styles.statBadge, { backgroundColor: `${dominantColor}20` }]}>
              <Ionicons name="trending-up" size={14} color={darkColor} />
              <Text style={[styles.popularity, { color: darkColor }]}>
                {Math.round(song.popularity || song.metadata?.popularity || 0)}%
              </Text>
            </View>
          ) : null}
        </View>

        {isTopCard ? (
          <View style={styles.previewContainer}>
            {song.preview_url ? (
              <View style={styles.musicPlayerContainer}>
                <View style={styles.playerControls}>
                  <TouchableOpacity 
                    style={styles.skipButton} 
                    onPress={skipBackward}
                    activeOpacity={0.7}
                  >
                    <MaterialIcons name="replay-10" size={24} color="#666" />
                  </TouchableOpacity>
                  <TouchableOpacity 
                    style={[
                      styles.pauseButton,
                      isPlaying && styles.pauseButtonActive,
                    ]} 
                    onPress={isPlaying ? stopPreview : playPreview}
                    activeOpacity={0.8}
                  >
                    <Animated.View style={{ transform: [{ scale: isPlaying ? pulseValue : 1 }] }}>
                      <Ionicons name={isPlaying ? "pause" : "play"} size={28} color="white" />
                    </Animated.View>
                  </TouchableOpacity>
                  <TouchableOpacity 
                    style={styles.skipButton} 
                    onPress={skipForward}
                    activeOpacity={0.7}
                  >
                    <MaterialIcons name="forward-10" size={24} color="#666" />
                  </TouchableOpacity>
                </View>
                <View style={styles.progressContainer}>
                  <View style={styles.progressBar}>
                    <Animated.View 
                      style={[
                        styles.progressFill, 
                        { 
                          width: progressWidth.interpolate({
                            inputRange: [0, 100],
                            outputRange: ['0%', '100%'],
                          }),
                          backgroundColor: dominantColor,
                        },
                      ]} 
                    />
                  </View>
                  <Text style={[styles.timeText, { color: darkColor }]}>
                    {Math.floor(currentTime)}s / {Math.floor(duration)}s
                  </Text>
                </View>
              </View>
            ) : (
              <View style={styles.noPreviewContainer}>
                <Ionicons name="musical-notes-outline" size={32} color={darkColor} style={{ opacity: 0.5 }} />
                <Text style={[styles.noPreviewText, { color: darkColor }]}>No preview available</Text>
              </View>
            )}
          </View>
        ) : null}
      </View>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: 30,
    padding: 24,
    margin: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 12,
    flex: 1,
    overflow: 'hidden',
    position: 'relative',
  },
  gradientOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    borderRadius: 30,
    zIndex: 0,
  },
  imageContainer: {
    width: '100%',
    height: 320,
    borderRadius: 20,
    marginBottom: 20,
    overflow: 'hidden',
    position: 'relative',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  imageGradient: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: '40%',
    backgroundColor: 'transparent',
    ...(Platform.OS === 'web' ? {
      background: 'linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 100%)',
    } : {}),
  },
  content: {
    flex: 1,
    zIndex: 1,
  },
  titleContainer: {
    marginBottom: 8,
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    marginBottom: 8,
    letterSpacing: -0.5,
  },
  titleUnderline: {
    height: 3,
    width: 60,
    borderRadius: 2,
    marginTop: 4,
  },
  artist: {
    fontSize: 20,
    marginBottom: 6,
    fontWeight: '600',
  },
  album: {
    fontSize: 16,
    marginBottom: 20,
    fontWeight: '500',
  },
  stats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
    gap: 12,
  },
  statBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    gap: 6,
  },
  popularityBadge: {
    backgroundColor: '#f5f5f5',
  },
  statDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  matchScore: {
    fontSize: 15,
    fontWeight: '700',
  },
  popularity: {
    fontSize: 15,
    fontWeight: '600',
    marginLeft: 4,
  },
  previewContainer: {
    marginBottom: 20,
  },
  playButton: {
    backgroundColor: '#2196F3',
    padding: 12,
    borderRadius: 25,
    alignItems: 'center',
    marginBottom: 0,
  },
  playButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  noPreviewContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 20,
    paddingHorizontal: 20,
  },
  noPreviewText: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
    marginTop: 8,
  },
  musicPlayerContainer: {
    marginTop: 15,
    backgroundColor: 'rgba(248, 248, 248, 0.95)',
    borderRadius: 20,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  playerControls: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    gap: 24,
  },
  skipButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'white',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  skipButtonText: {
    fontSize: 18,
  },
  pauseButton: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#2196F3',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#2196F3',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 6,
  },
  pauseButtonActive: {
    backgroundColor: '#1976D2',
    shadowColor: '#1976D2',
  },
  pauseButtonText: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
  },
  progressContainer: {
    marginTop: 0,
    marginBottom: 0,
  },
  progressBar: {
    height: 6,
    backgroundColor: '#e0e0e0',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  timeText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    fontWeight: '600',
  },
});