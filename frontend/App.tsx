import React from 'react';
import { StatusBar } from 'expo-status-bar';
import RootNavigator from './src/navigation/RootNavigator';

/**
 * App - Entry point for the application
 *
 * Simple setup:
 * - Renders navigation
 * - Sets status bar to light (white text for dark UI)
 */
export default function App() {
  return (
    <>
      <StatusBar style="light" />
      <RootNavigator />
    </>
  );
}
