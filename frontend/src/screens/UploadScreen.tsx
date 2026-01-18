import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { uploadPDF } from '../services/api';
import { RootStackParamList } from '../navigation/types';

type UploadScreenProps = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Upload'>;
};

/**
 * UploadScreen - Allows users to select and upload a PDF
 *
 * Flow:
 * 1. User taps "Select PDF" button
 * 2. Document picker opens
 * 3. After selection, PDF is uploaded to backend
 * 4. On success, navigate to Processing screen with job_id
 */
export default function UploadScreen({ navigation }: UploadScreenProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  const handlePickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'application/pdf',
        copyToCacheDirectory: true,
      });

      if (result.canceled) {
        return;
      }

      const file = result.assets[0];
      setSelectedFile(file.name);

      // Immediately start upload after selection
      await handleUpload(file.uri, file.name);
    } catch (error) {
      Alert.alert('Error', 'Failed to pick document');
      console.error(error);
    }
  };

  const handleUpload = async (uri: string, fileName: string) => {
    setIsUploading(true);

    try {
      const response = await uploadPDF(uri, fileName);

      // Navigate to processing screen with job_id
      navigation.navigate('Processing', { jobId: response.job_id });
    } catch (error) {
      Alert.alert('Upload Failed', 'Could not upload PDF. Please try again.');
      console.error(error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Upload Lecture Notes</Text>
        <Text style={styles.subtitle}>
          Select a PDF of your lecture slides to generate video summaries
        </Text>

        <TouchableOpacity
          style={[styles.button, isUploading && styles.buttonDisabled]}
          onPress={handlePickDocument}
          disabled={isUploading}
        >
          {isUploading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Select PDF</Text>
          )}
        </TouchableOpacity>

        {selectedFile && (
          <Text style={styles.fileName}>Selected: {selectedFile}</Text>
        )}

        {isUploading && (
          <Text style={styles.uploadingText}>Uploading and processing...</Text>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#999',
    marginBottom: 48,
    textAlign: 'center',
    lineHeight: 24,
  },
  button: {
    backgroundColor: '#ff0050',
    paddingHorizontal: 48,
    paddingVertical: 16,
    borderRadius: 8,
    minWidth: 200,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#666',
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  fileName: {
    color: '#fff',
    marginTop: 24,
    fontSize: 14,
  },
  uploadingText: {
    color: '#999',
    marginTop: 16,
    fontSize: 14,
  },
});
