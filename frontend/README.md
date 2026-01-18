# MR Team - Frontend

React Native mobile app for generating AI video summaries from PDF lecture notes.

## Project Structure

```
frontend/
├── App.tsx                          # Entry point
├── app.json                         # Expo configuration
├── package.json                     # Dependencies
├── tsconfig.json                    # TypeScript config
├── assets/                          # App icons and splash screens
└── src/
    ├── config.ts                    # API base URL configuration
    ├── types.ts                     # TypeScript interfaces
    ├── services/
    │   └── api.ts                   # API calls (upload, fetch feed)
    ├── navigation/
    │   ├── types.ts                 # Navigation types
    │   └── RootNavigator.tsx        # Stack navigator
    ├── screens/
    │   ├── UploadScreen.tsx         # PDF upload screen
    │   └── FeedScreen.tsx           # TikTok-style video feed
    └── components/
        └── VideoPlayer.tsx          # Video player with autoplay
```

## Setup

### Option A: Frontend-Only Demo (Recommended for Testing)

1. **Start the mock backend:**
   ```bash
   cd mock-backend
   npm install
   npm start
   ```

2. **Configure frontend to use mock backend:**
   ```bash
   cd frontend
   ```

   Edit `src/config.ts`:
   ```typescript
   // For iOS Simulator or Android Emulator
   export const API_BASE_URL = 'http://localhost:5000';

   // For physical device (replace with your machine's IP)
   export const API_BASE_URL = 'http://192.168.1.x:5000';
   ```

   To find your IP:
   - Mac: `ifconfig | grep "inet " | grep -v 127.0.0.1`
   - Windows: `ipconfig`

3. **Install and run the app:**
   ```bash
   npm install
   npm start
   ```

   Then press:
   - `i` for iOS Simulator
   - `a` for Android Emulator
   - Or scan QR code with Expo Go on your phone

### Option B: With Real Backend

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure backend URL:**
   Edit `src/config.ts` and update `API_BASE_URL` with your backend URL.

3. **Run the app:**
   ```bash
   npm start
   ```

## Demo Workflow

### Prerequisites
- Backend server running and accessible
- Expo Go app installed on demo device OR iOS Simulator/Android Emulator running
- Sample PDF file ready (lecture slides or notes)

### Step-by-Step Demo

#### 1. **Start Backend**
```bash
cd backend
# Start your backend server (exact command depends on backend implementation)
python app.py  # or npm start, or whatever your backend uses
```

Make sure backend is accessible at the URL configured in `frontend/src/config.ts`.

#### 2. **Update Backend URL (if needed)**
If demoing on physical device, update `frontend/src/config.ts`:
```typescript
// Use your machine's local IP (not localhost)
export const API_BASE_URL = 'http://192.168.1.x:5000';  // Replace with your IP
```

To find your IP:
- Mac: `ifconfig | grep "inet " | grep -v 127.0.0.1`
- Windows: `ipconfig`

#### 3. **Start Frontend**
```bash
cd frontend
npm start
```

This opens Expo DevTools in your browser.

#### 4. **Launch on Device**
- **iOS Simulator:** Press `i` in terminal
- **Android Emulator:** Press `a` in terminal
- **Physical Device:** Scan QR code with Expo Go app

#### 5. **Demo Flow**

**Upload Screen:**
1. App opens to black screen with "Upload Lecture Notes" title
2. Tap "Select PDF" button
3. Choose a PDF from device (prepare one beforehand)
4. App shows "Uploading and processing..." message
5. Once upload completes, automatically navigates to feed

**Feed Screen:**
6. Videos appear in TikTok-style vertical feed
7. First video auto-plays immediately
8. Swipe up to see next video (current pauses, next plays)
9. Caption appears at bottom of each video
10. As you approach end of videos, more are fetched automatically (if available)

### Tips for Smooth Demo

1. **Pre-process a PDF before demo**
   - Upload a PDF ahead of time to have videos ready
   - This avoids waiting for video generation during demo

2. **Test network connectivity**
   - Ensure phone/emulator can reach backend
   - Use `curl http://YOUR_IP:PORT/api/feed?job_id=test` to verify

3. **Have backup videos**
   - If live processing fails, have a pre-generated job_id ready
   - You can hardcode a job_id temporarily in `UploadScreen.tsx` to skip upload

4. **Prepare talking points:**
   - "Upload any lecture PDF"
   - "AI generates bite-sized video summaries"
   - "Swipe through like TikTok - perfect for quick revision"
   - "Videos auto-generated from slide content"

### Troubleshooting

**Videos won't load:**
- Check `src/config.ts` has correct backend URL
- Verify backend is running: `curl http://YOUR_BACKEND_URL/api/feed?job_id=test`
- Check network requests in Expo DevTools

**Upload fails:**
- Ensure backend accepts multipart/form-data at `/api/pdf`
- Check CORS settings if backend on different host
- Verify PDF file size limits on backend

**Videos don't autoplay:**
- iOS may require user interaction first (tap screen once)
- Check video URLs are publicly accessible
- Try with a test video URL first

## Key Features

- **PDF Upload:** Select lecture notes from device
- **TikTok-Style Feed:** Vertical swipe with autoplay
- **Auto-pagination:** Fetches more videos as you scroll
- **Clean UI:** Dark theme, fullscreen videos, caption overlays

## Tech Stack

- React Native + Expo
- TypeScript
- expo-document-picker (PDF selection)
- react-native-pager-view (vertical swipe)
- expo-av (video playback)
- React Navigation (routing)
