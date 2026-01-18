import React, { useEffect, useState, useRef } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, ActivityIndicator } from 'react-native';
import UploadScreen from '../screens/UploadScreen';
import ProcessingScreen from '../screens/ProcessingScreen';
import FeedScreen from '../screens/FeedScreen';
import { RootStackParamList } from './types';
import { getJobIds } from '../services/storage';

const Stack = createNativeStackNavigator<RootStackParamList>();

/**
 * RootNavigator - Main navigation structure with session persistence
 *
 * Three screens:
 * 1. Upload - Initial screen for PDF selection
 * 2. Processing - Status polling screen with progress bar (receives jobId as param)
 * 3. Feed - Video feed screen (receives jobId as param)
 *
 * Session Persistence:
 * - On startup, checks AsyncStorage for saved job_ids
 * - If found, navigates directly to Feed with the first job_id
 * - If not found, shows Upload screen (first-time users)
 *
 * All screens use dark theme with hidden headers for immersive experience
 */
export default function RootNavigator() {
  const [isReady, setIsReady] = useState(false);
  const [initialRoute, setInitialRoute] = useState<'Upload' | 'Feed'>('Upload');
  const [initialJobId, setInitialJobId] = useState<string | undefined>(undefined);
  const navigationRef = useRef<any>(null);

  useEffect(() => {
    checkSavedSession();
  }, []);

  const checkSavedSession = async () => {
    try {
      const savedJobIds = await getJobIds();

      if (savedJobIds.length > 0) {
        // User has a saved session, navigate to Feed with first job_id
        setInitialRoute('Feed');
        setInitialJobId(savedJobIds[0]);
      } else {
        // No saved session, show Upload screen
        setInitialRoute('Upload');
      }
    } catch (error) {
      console.error('Error checking saved session:', error);
      // On error, default to Upload screen
      setInitialRoute('Upload');
    } finally {
      setIsReady(true);
    }
  };

  // Show loading screen while checking for saved session
  if (!isReady) {
    return (
      <View style={{ flex: 1, backgroundColor: '#000', justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#fff" />
      </View>
    );
  }

  return (
    <NavigationContainer ref={navigationRef}>
      <Stack.Navigator
        initialRouteName={initialRoute}
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: '#000' },
          animation: 'fade',
        }}
      >
        <Stack.Screen name="Upload" component={UploadScreen} />
        <Stack.Screen name="Processing" component={ProcessingScreen} />
        <Stack.Screen
          name="Feed"
          component={FeedScreen}
          initialParams={initialJobId ? { jobId: initialJobId } : undefined}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
