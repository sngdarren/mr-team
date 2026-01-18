import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';
import { checkJobStatus } from '../services/api';
import { JobStatus } from '../types';
import { saveJobId } from '../services/storage';

type Props = NativeStackScreenProps<RootStackParamList, 'Processing'>;

export default function ProcessingScreen({ route, navigation }: Props) {
  const { jobId } = route.params;
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<JobStatus>('processing');
  const [message, setMessage] = useState('Analyzing PDF...');
  const [estimatedTime, setEstimatedTime] = useState<number | undefined>();
  const pollingInterval = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Start polling immediately
    pollStatus();

    // Set up polling interval (every 5 seconds)
    pollingInterval.current = setInterval(() => {
      pollStatus();
    }, 5000);

    // Cleanup on unmount
    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    };
  }, [jobId]);

  const pollStatus = async () => {
    try {
      const statusResponse = await checkJobStatus(jobId);

      setProgress(statusResponse.progress);
      setStatus(statusResponse.status);
      if (statusResponse.message) {
        setMessage(statusResponse.message);
      }
      if (statusResponse.estimated_time_remaining !== undefined) {
        setEstimatedTime(statusResponse.estimated_time_remaining);
      }

      // Handle completion
      if (statusResponse.status === 'done') {
        if (pollingInterval.current) {
          clearInterval(pollingInterval.current);
        }
        // Save job_id for session persistence
        await saveJobId(jobId);
        // Navigate to feed with job_id
        navigation.replace('Feed', { jobId });
      }

      // Handle failure
      if (statusResponse.status === 'failed') {
        if (pollingInterval.current) {
          clearInterval(pollingInterval.current);
        }
        Alert.alert(
          'Processing Failed',
          statusResponse.message || 'Video generation failed. Please try again.',
          [
            {
              text: 'Go Back',
              onPress: () => navigation.navigate('Upload'),
            },
          ]
        );
      }
    } catch (error) {
      console.error('Error polling status:', error);
      // Don't stop polling on network errors - keep trying
    }
  };

  const formatTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${Math.round(seconds)}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <ActivityIndicator size="large" color="#007AFF" style={styles.spinner} />

        <Text style={styles.title}>Processing Your PDF</Text>
        <Text style={styles.subtitle}>{message}</Text>

        {/* Progress Bar */}
        <View style={styles.progressContainer}>
          <View style={styles.progressBar}>
            <View style={[styles.progressFill, { width: `${progress}%` }]} />
          </View>
          <Text style={styles.progressText}>{Math.round(progress)}%</Text>
        </View>

        {/* Estimated Time */}
        {estimatedTime !== undefined && estimatedTime > 0 && (
          <Text style={styles.estimatedTime}>
            Estimated time remaining: {formatTime(estimatedTime)}
          </Text>
        )}

        <Text style={styles.hint}>
          This may take 2-3 minutes.{'\n'}
          We're generating amazing videos from your content!
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    alignItems: 'center',
    paddingHorizontal: 40,
    maxWidth: 400,
  },
  spinner: {
    marginBottom: 30,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#aaa',
    marginBottom: 30,
    textAlign: 'center',
  },
  progressContainer: {
    width: '100%',
    marginBottom: 20,
  },
  progressBar: {
    width: '100%',
    height: 8,
    backgroundColor: '#333',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 4,
  },
  progressText: {
    fontSize: 14,
    color: '#fff',
    textAlign: 'center',
  },
  estimatedTime: {
    fontSize: 14,
    color: '#888',
    marginTop: 10,
    marginBottom: 20,
    textAlign: 'center',
  },
  hint: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 20,
    lineHeight: 20,
  },
});
