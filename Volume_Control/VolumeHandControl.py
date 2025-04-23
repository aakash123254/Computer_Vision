import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Webcam Settings
wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)  # Use 0 instead of 1 if only one webcam is available
if not cap.isOpened():
    print("Error: Webcam not found!")
    exit()

cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

# Initialize Hand Detector
detector = htm.handDetector(detectionCon=0.7)  # Adjust detection confidence

# Initialize Volume Control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()

# Volume Variables
minVol = volRange[0]
maxVol = volRange[1]
volBar = 400
volPer = 0

while True:
    success, img = cap.read()
    if not success:
        print("Error: Failed to capture image")
        break

    try:
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        if len(lmList) > 8 and lmList[4] and lmList[8]:  # Check if required landmarks exist
            x1, y1 = lmList[4][1], lmList[4][2]  # Thumb Tip
            x2, y2 = lmList[8][1], lmList[8][2]  # Index Finger Tip
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # Center Between Thumb & Index

            # Draw UI Elements
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

            # Calculate Distance Between Thumb & Index
            length = math.hypot(x2 - x1, y2 - y1)
            print(f"Distance: {length}")  # Debug statement

            # Map Distance to Volume Range
            vol = np.interp(length, [50, 300], [minVol, maxVol])
            volPer = np.interp(length, [50, 300], [0, 100]) / 100  # Normalize to [0.0, 1.0]
            volBar = np.interp(length, [50, 300], [400, 150])

            # Smooth Volume Changes
            current_vol = volume.GetMasterVolumeLevelScalar()
            smoothed_vol = 0.9 * current_vol + 0.1 * volPer
            volume.SetMasterVolumeLevelScalar(smoothed_vol, None)

            print(f"Volume Set: {smoothed_vol}")  # Debug statement

            # Change Color when Volume is at Minimum
            if length < 50:
                cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    except Exception as e:
        print(f"Error: {e}")
        continue

    # Draw Volume Bar
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer * 100)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    # Display FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    # Show Image
    cv2.imshow("Volume Control", img)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting program...")
        break

    time.sleep(0.01)  # Reduce CPU usage

# Release Resources
cap.release()
cv2.destroyAllWindows()