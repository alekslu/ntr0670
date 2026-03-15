# Camera Project (WSL2 + Windows USB Camera Bridge)

This repository captures a single image from a USB camera while running orchestration from WSL2.
Camera access is done on Windows Python, and output is written directly to the shared project folder.

## Why this structure
- WSL controls workflow.
- Windows handles camera device access.
- Output is stored in one Git workspace.
- No manual file movement between separate folders.

## Project layout
- windows_scripts/camera_win.py: Windows-side OpenCV capture script.
- wsl_scripts/capture_wsl.py: WSL launcher and path bridge.
- output/: generated image artifacts.
- docs/spec.md: eestikeelne ulevaade, mis muudeti ja kuidas voog toole pandi.

## Prerequisites
- WSL2 Ubuntu environment.
- Windows Python available as python.exe from WSL.
- OpenCV installed in Windows Python environment.
- wslpath available in WSL.

## Setup
Install OpenCV for the Windows interpreter:

```bash
python.exe -m pip install opencv-python
```

Optional check:

```bash
python.exe -c "import cv2; print(cv2.__version__)"
```

## Run capture
From repository root in WSL:

```bash
python3 wsl_scripts/capture_wsl.py
```

Expected result:
- output/webcam.png is created or updated.
- command exits with code 0 on success.

## Troubleshooting
python.exe not found:
- Ensure Windows Python is installed and available to WSL PATH.
- Test with: python.exe --version

OpenCV import error:
- Reinstall dependency in Windows Python:

```bash
python.exe -m pip install --upgrade pip opencv-python
```

Camera open failure:
- Verify camera is not occupied by another app.
- Try explicit index test:

```bash
python.exe windows_scripts/camera_win.py --cam-index 0 --output C:\\temp\\test.png
```

## Documentation workflow
1. Update docs/spec.md when workflow or behavior changes.
2. Keep README run instructions in sync with script behavior.
3. Validate by running capture command end-to-end.
4. Commit code and docs in the same change set.

## Git quick start
```bash
git add .
git commit -m "Update camera bridge docs and usage guide"
```
