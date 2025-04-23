import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import HandTrackingModule as htm

# Set webcam size
wCam, hCam = 1280, 720  # Keep a higher resolution for better tracking

# Initialize the webcam
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# Initialize the hand detector
detector = htm.HandDetector(maxHands=1, detectionCon=0.7)

# Get screen size for controlling the mouse
screen_w, screen_h = pyautogui.size()

# Smoothing factor for cursor movement
smoothening = 7
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0

# Adjusted margins to allow full-screen movement
MARGIN_X = 80  # Adjust for left/right movement
MARGIN_Y = 60  # Adjust for top/bottom movement

#Variables for FPS Calculation 
prev_time=0

while True:
    # Read the frame from the webcam
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    
    #FPS Calculation 
    curr_time = time.time()
    fps = 1/(curr_time-prev_time)
    prev_time = curr_time 
    
    #Display FPS on screen 
    cv2.putText(img,f'FPS:{int(fps)}',(20,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),3)

    if len(lmList) != 0:
        # Get coordinates of index finger
        x1, y1 = lmList[8][1], lmList[8][2]  # Index finger tip

        # Find which fingers are up
        fingers = detector.fingersUp()

        # Move Mouse (Index finger Up)
        if fingers[1] == 1 and fingers[2] == 0:
            # Adjusted coordinate mapping for full-screen coverage
            screen_x = np.interp(x1, (MARGIN_X, wCam - MARGIN_X), (screen_w, 0))  
            screen_y = np.interp(y1, (MARGIN_Y, hCam - MARGIN_Y), (0, screen_h))  

            # Smooth cursor movement
            curr_x = prev_x + (screen_x - prev_x) / smoothening
            curr_y = prev_y + (screen_y - prev_y) / smoothening

            # Move the mouse cursor
            pyautogui.moveTo(curr_x, curr_y)

            prev_x, prev_y = curr_x, curr_y

        # Click the Mouse (Index and middle finger up)
        if fingers[1] == 1 and fingers[2] == 1:
            length = np.hypot(lmList[12][1] - x1, lmList[12][2] - y1)
            if length < 40:
                pyautogui.click()
                time.sleep(0.2)

    # Display the video feed
    cv2.imshow("Virtual Mouse", img)
    cv2.waitKey(1)
