import React, { useEffect, useState, useCallback, useRef } from 'react';
import { View, StyleSheet, ActivityIndicator, Text, Platform, TouchableOpacity, Alert } from 'react-native';
import { RouteProp, useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import * as DocumentPicker from 'expo-document-picker';
import { fetchFeed, uploadPDF, checkJobStatus, JobNotFoundError } from '../services/api';
import { Video } from '../types';
import VideoPlayer from '../components/VideoPlayer';
import { RootStackParamList } from '../navigation/types';
import { saveJobId } from '../services/storage';

// Platform-specific imports
// On web, use custom ScrollView-based pager
// On native, use react-native-pager-view
let PagerView: any;
let PagerViewOnPageSelectedEvent: any;

if (Platform.OS === 'web') {
  const WebPagerView = require('../components/PagerView.web').default;
  PagerView = WebPagerView;
  PagerViewOnPageSelectedEvent = require('../components/PagerView.web').PagerViewOnPageSelectedEvent;
} else {
  PagerView = require('react-native-pager-view').default;
  PagerViewOnPageSelectedEvent = require('react-native-pager-view').PagerViewOnPageSelectedEvent;
}

type FeedScreenProps = {
  route: RouteProp<RootStackParamList, 'Feed'>;
};

type FeedScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Feed'>;

interface ProcessingJob {
  jobId: string;
  intervalId: NodeJS.Timeout;
}

/**
 * FeedScreen - TikTok-style vertical video feed with background upload
 *
 * Key features:
 * - Vertical swipe using react-native-pager-view
 * - Only the currently visible video plays (others are paused)
 * - Infinite scroll: fetch more videos when approaching the end
 * - Pagination using cursor from API
 * - Floating Action Button (FAB) for uploading more PDFs
 * - Background processing: stay in feed while new videos are being generated
 * - Auto-append: new videos automatically added to the queue when ready
 */
export default function FeedScreen({ route }: FeedScreenProps) {
  const { jobId } = route.params;
  const navigation = useNavigation<FeedScreenNavigationProp>();

  const [videos, setVideos] = useState<Video[]>([]);
  const [currentPage, setCurrentPage] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [nextCursor, setNextCursor] = useState<string | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  const [isJobNotFound, setIsJobNotFound] = useState(false);
  const [processingJobs, setProcessingJobs] = useState<ProcessingJob[]>([]);
  const [jobIds, setJobIds] = useState<string[]>([jobId]);

  const pagerRef = useRef<typeof PagerView>(null);

  // Initial fetch
  useEffect(() => {
    loadVideos();
  }, []);

  // Cleanup polling intervals on unmount
  useEffect(() => {
    return () => {
      processingJobs.forEach(job => clearInterval(job.intervalId));
    };
  }, [processingJobs]);

  // Pagination: fetch more when user is near the end
  useEffect(() => {
    const threshold = 2; // Start loading when 2 videos away from end

    if (videos.length > 0 && currentPage >= videos.length - threshold) {
      if (nextCursor && !isLoadingMore) {
        loadMoreVideos();
      }
    }
  }, [currentPage, videos.length, nextCursor, isLoadingMore]);

  const loadVideos = async () => {
    try {
      setIsLoading(true);
      setError(null);
      setIsJobNotFound(false);
      console.log('Fetching feed for job:', jobIds);
      const response = await fetchFeed(jobId);

      setVideos(response.videos);
      setNextCursor(response.next_cursor);
    } catch (err) {
      if (err instanceof JobNotFoundError) {
        setError('Job not found. Please upload a new PDF.');
        setIsJobNotFound(true);
      } else {
        setError('Failed to load videos. Please try again.');
      }
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMoreVideos = async () => {
    if (!nextCursor || isLoadingMore) return;

    try {
      setIsLoadingMore(true);

      const response = await fetchFeed(jobId, nextCursor);

      setVideos((prev) => [...prev, ...response.videos]);
      setNextCursor(response.next_cursor);
    } catch (err) {
      console.error('Failed to load more videos:', err);
    } finally {
      setIsLoadingMore(false);
    }
  };

  /**
   * Handle upload button press - open document picker and upload in background
   */
  const handleUploadMore = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'application/pdf',
        copyToCacheDirectory: true,
      });

      if (result.canceled) {
        return;
      }

      const file = result.assets[0];

      // Upload PDF and get job_id
      const uploadResponse = await uploadPDF(file.uri, file.name);
      const newJobId = uploadResponse.job_id;

      // Add to job list
      setJobIds([...jobIds, newJobId]);

      // Start background polling for this job
      startBackgroundPolling(newJobId);

      // Optional: Show a subtle toast/notification
      console.log(`Background processing started for job: ${newJobId}`);
    } catch (error) {
      Alert.alert('Upload Failed', 'Could not upload PDF. Please try again.');
      console.error(error);
    }
  };

  /**
   * Start polling for a job in the background
   */
  const startBackgroundPolling = (newJobId: string) => {
    const intervalId = setInterval(async () => {
      try {
        const statusResponse = await checkJobStatus(newJobId);

        if (statusResponse.status === 'done') {
          // Job complete! Fetch the new videos and append them
          clearInterval(intervalId);

          // Remove from processing jobs
          setProcessingJobs(prev => prev.filter(job => job.jobId !== newJobId));

          // Fetch videos for this job
          const feedResponse = await fetchFeed(newJobId);

          // Append new videos to the end of the list
          setVideos(prev => [...prev, ...feedResponse.videos]);

          // Save job_id to storage for session persistence
          await saveJobId(newJobId);

          console.log(`New videos added from job: ${newJobId}`);
        } else if (statusResponse.status === 'failed') {
          // Job failed
          clearInterval(intervalId);
          setProcessingJobs(prev => prev.filter(job => job.jobId !== newJobId));
          console.error(`Job failed: ${newJobId}`);
        }
      } catch (error) {
        console.error('Error polling job status:', error);
        // Don't clear interval on network errors - keep trying
      }
      
    }, 5000); // Poll every 5 seconds

    // Add to processing jobs list
    setProcessingJobs(prev => [...prev, { jobId: newJobId, intervalId }]);
  };

  const handlePageSelected = useCallback((e: typeof PagerViewOnPageSelectedEvent) => {
    setCurrentPage(e.nativeEvent.position);
  }, []);

  // Loading state
  if (isLoading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#fff" />
        <Text style={styles.loadingText}>Loading videos...</Text>
      </View>
    );
  }

  // Error state
  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>{error}</Text>
        {isJobNotFound && (
          <TouchableOpacity
            style={styles.uploadButton}
            onPress={() => navigation.navigate('Upload')}
            activeOpacity={0.8}
          >
            <Text style={styles.uploadButtonText}>Upload New PDF</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  }

  // Empty state
  if (videos.length === 0) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.emptyText}>No videos available yet.</Text>
        <Text style={styles.emptySubtext}>
          Your videos are being generated. Check back soon!
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <PagerView
        ref={pagerRef}
        style={styles.pager}
        initialPage={0}
        orientation="vertical"
        onPageSelected={handlePageSelected}
      >
        {videos.map((video, index) => (
          <View key={video.id} style={styles.page}>
            <VideoPlayer video={video} isActive={index === currentPage} />
          </View>
        ))}
      </PagerView>

      {/* Floating Action Button - Upload More PDFs */}
      <TouchableOpacity
        style={styles.fab}
        onPress={handleUploadMore}
        activeOpacity={0.8}
      >
        <Text style={styles.fabIcon}>+</Text>
      </TouchableOpacity>

      {/* Loading indicator for pagination */}
      {isLoadingMore && (
        <View style={styles.loadingMoreContainer}>
          <ActivityIndicator size="small" color="#fff" />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  pager: {
    flex: 1,
  },
  page: {
    flex: 1,
  },
  centerContainer: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  loadingText: {
    color: '#fff',
    fontSize: 16,
    marginTop: 16,
  },
  errorText: {
    color: '#ff0050',
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
  },
  emptyText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 8,
  },
  emptySubtext: {
    color: '#999',
    fontSize: 14,
    textAlign: 'center',
  },
  loadingMoreContainer: {
    position: 'absolute',
    bottom: 32,
    alignSelf: 'center',
  },
  fab: {
    position: 'absolute',
    top: 48,
    right: 20,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(255, 0, 80, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  fabIcon: {
    color: '#fff',
    fontSize: 32,
    fontWeight: '300',
    lineHeight: 32,
  },
  uploadButton: {
    marginTop: 24,
    backgroundColor: '#ff0050',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 8,
  },
  uploadButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
