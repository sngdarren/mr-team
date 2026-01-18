# Assets Placeholder

The app needs the following image files in this directory:

- `icon.png` - 1024x1024px (App icon)
- `splash.png` - 1284x2778px (Splash screen)
- `adaptive-icon.png` - 1024x1024px (Android adaptive icon)
- `favicon.png` - 48x48px (Web favicon)

## Quick Fix: Generate Placeholder Images

You can use any of these methods to create placeholder images:

### Option 1: Using online tools
Visit https://placeholder.com/ and create:
- icon.png: 1024x1024
- splash.png: 1284x2778
- adaptive-icon.png: 1024x1024
- favicon.png: 48x48

### Option 2: Copy from Expo template
```bash
npx create-expo-app temp-app
cp temp-app/assets/* ./assets/
rm -rf temp-app
```

### Option 3: Use a simple color image
Create any PNG files with the sizes above. The app will run fine with placeholder images.

## Note
Missing asset files will show warnings but won't prevent the app from running.
