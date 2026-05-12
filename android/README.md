# Android App

This project packages `../livre/xhtml/` as an offline Android WebView app.

## Build

```bash
cd android
./gradlew assembleDebug
```

The generated APK is written to `app/build/outputs/apk/debug/app-debug.apk`.

## Refresh Book Assets

Regenerate the XHTML from the repository root, then copy it into the Android asset folder:

```bash
python3 livre/build_xhtml.py
cd android
./gradlew assembleDebug
```

The Gradle build syncs `livre/xhtml/` into `app/src/main/assets/book/` automatically.
