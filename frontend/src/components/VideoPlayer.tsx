import React, { useEffect, useRef, useState } from 'react';
import { View, StyleSheet, Dimensions, Text, ActivityIndicator } from 'react-native';
import { Video, ResizeMode, AVPlaybackStatus } from 'expo-av';
import { Video as VideoType } from '../types';

const { width, height } = Dimensions.get('window');

interface VideoPlayerProps {
  video: VideoType;
  isActive: boolean; // Whether this video is currently visible
}

/**
 * VideoPlayer - Handles individual video playback
 *
 * Key features:
 * - Autoplay when isActive becomes true
 * - Pause when isActive becomes false
 * - Loop video playback
 * - Show loading state
 * - Display caption overlay
 *
 * Why expo-av?
 * - Built-in support for remote video URLs
 * - Simple imperative API (play/pause)
 * - Works reliably on both iOS and Android
 */
export default function VideoPlayer({ video, isActive }: VideoPlayerProps) {
  const videoRef = useRef<Video>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Handle autoplay/pause based on visibility
  useEffect(() => {
    if (!videoRef.current) return;

    if (isActive) {
      videoRef.current.playAsync();
    } else {
      videoRef.current.pauseAsync();
    }
  }, [isActive]);

  const handlePlaybackStatusUpdate = (status: AVPlaybackStatus) => {
    if (status.isLoaded) {
      setIsLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Video
        ref={videoRef}
        source={{ uri: video.video_url }}
        style={styles.video}
        resizeMode={ResizeMode.COVER}
        shouldPlay={isActive}
        isLooping
        onPlaybackStatusUpdate={handlePlaybackStatusUpdate}
      />

      {isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#fff" />
        </View>
      )}

      {/* Caption overlay at bottom */}
      <View style={styles.captionContainer}>
        <Text style={styles.caption}>{video.caption}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width,
    height,
    backgroundColor: '#000',
  },
  video: {
    width: '100%',
    height: '100%',
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  captionContainer: {
    position: 'absolute',
    bottom: 80,
    left: 16,
    right: 16,
  },
  caption: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    textShadowColor: 'rgba(0, 0, 0, 0.75)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
  },
});
