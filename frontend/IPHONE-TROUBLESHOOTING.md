# iPhone Demo Troubleshooting Guide

## Common Errors and Solutions

### 1. "Unable to connect to Metro bundler"

**Cause**: iPhone can't reach your Mac

**Solutions**:
- ✅ Ensure iPhone and Mac are on the **same WiFi network**
- ✅ Check Mac's firewall isn't blocking port 8081
- ✅ Verify your Mac's IP in the QR code is correct

**Fix**:
```bash
# Find your Mac's IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# Restart with tunnel (slower but works through any network)
npx expo start --tunnel
```

---

### 2. "Incompatible Expo SDK version"

**Cause**: Expo Go app version doesn't match SDK 54

**Solution**:
- Update Expo Go app from App Store
- Or check what SDK version your Expo Go supports
- SDK 54 requires Expo Go v2.32.0 or later

---

### 3. "Network request failed" or API errors

**Cause**: App can't reach mock backend at localhost

**Solution**:
Update `src/config.ts` with your Mac's actual IP:

```typescript
// Don't use localhost - iPhone can't reach it
// export const API_BASE_URL = 'http://localhost:3000';

// Use your Mac's IP instead
export const API_BASE_URL = 'http://192.168.1.x:3000';
```

Find your IP:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

---

### 4. "Error: Unable to resolve module"

**Cause**: Missing dependencies or cache issues

**Solution**:
```bash
# Clear cache and reinstall
rm -rf node_modules
npm install
npx expo start -c
```

---

### 5. "Invariant Violation" or React errors

**Cause**: React 19 compatibility issues

**Check**: Are you seeing errors about hooks, context, or components?

**Solution**: This is why we need to see your specific error!

---

### 6. Video/Document picker not working

**Cause**: iOS permissions or native module issues

**Note**: Some native modules work differently in Expo Go vs standalone builds

**Workaround**:
- expo-document-picker should work in Expo Go
- expo-av video playback should work
- If not, you may need to build a development build

---

## How to Share Your Error

Please provide:

1. **Screenshot of error** on iPhone
2. **Terminal output** when the error occurs
3. **Which screen** - Upload screen or Feed screen?

### To see detailed errors:

1. **In Terminal** (where you ran `npm start`):
   - Look for red error messages
   - Copy the full stack trace

2. **In Expo Go app**:
   - Shake your iPhone
   - Tap "Show Developer Menu"
   - Tap "Debug Remote JS"
   - Errors will show in Safari

3. **Metro bundler logs**:
   ```bash
   npm start
   # Look for any red text or "ERROR" messages
   ```

---

## Quick Diagnostic

Run this to start fresh:

```bash
# 1. Kill all processes
lsof -ti:8081 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# 2. Clear Expo cache
npx expo start -c

# 3. In Expo Go app on iPhone:
#    - Shake device
#    - Clear cache
#    - Try again
```

---

## Alternative: Use Tunnel Mode

If WiFi connection is problematic:

```bash
# Install tunnel
npm install -g @expo/ngrok

# Start with tunnel
npx expo start --tunnel
```

This works over the internet, no WiFi required!

---

## What to Check Right Now

1. **Is mock backend running?**
   ```bash
   cd mock-backend
   npm start
   # Should show: 🚀 Mock Backend Server Running
   ```

2. **Is frontend using correct IP?**
   ```bash
   cat src/config.ts | grep API_BASE_URL
   # Should show your Mac's IP, not localhost
   ```

3. **Is Metro bundler running?**
   ```bash
   # Should see: Metro waiting on exp://...
   ```

---

## Next Steps

**Please share**:
- The exact error message from your iPhone
- Screenshot if possible
- What were you doing when it happened (opening app, uploading PDF, etc.)

Then I can give you the exact fix!
