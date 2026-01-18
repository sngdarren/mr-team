import AsyncStorage from '@react-native-async-storage/async-storage';

const JOB_IDS_KEY = 'job_ids';

/**
 * Save a new job_id to the stored list
 */
export async function saveJobId(jobId: string): Promise<void> {
  try {
    const existingIds = await getJobIds();
    const updatedIds = [...existingIds, jobId];
    await AsyncStorage.setItem(JOB_IDS_KEY, JSON.stringify(updatedIds));
  } catch (error) {
    console.error('Error saving job_id:', error);
  }
}

/**
 * Get all saved job_ids
 */
export async function getJobIds(): Promise<string[]> {
  try {
    const savedIds = await AsyncStorage.getItem(JOB_IDS_KEY);
    if (savedIds) {
      return JSON.parse(savedIds);
    }
    return [];
  } catch (error) {
    console.error('Error getting job_ids:', error);
    return [];
  }
}

/**
 * Clear all saved job_ids
 */
export async function clearJobIds(): Promise<void> {
  try {
    await AsyncStorage.removeItem(JOB_IDS_KEY);
  } catch (error) {
    console.error('Error clearing job_ids:', error);
  }
}

/**
 * Check if there are any saved job_ids
 */
export async function hasSavedSession(): Promise<boolean> {
  const jobIds = await getJobIds();
  return jobIds.length > 0;
}
