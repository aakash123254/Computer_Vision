import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import HandTrackingModule as htm

# Set webcam size
wCam, hCam = 1280, 720  

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
MARGIN_X = 80  
MARGIN_Y = 60  

# Variables for FPS Calculation 
prev_time = 0

# Scroll settings
SCROLL_SPEED = 50  
CLOSE_DISTANCE = 30  # If fingers are close together
OPEN_DISTANCE = 80  # If fingers are spread apart

while True:
    # Read the frame from the webcam
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    
    # FPS Calculation 
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time 
    
    # Display FPS on screen 
    cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    if len(lmList) != 0:
        # Get coordinates of index finger and thumb
        x1, y1 = lmList[8][1], lmList[8][2]  # Index finger tip
        x_thumb, y_thumb = lmList[4][1], lmList[4][2]  # Thumb tip
        y_index_base = lmList[5][2]  # Base of index finger (for volume detection)

        # Find which fingers are up
        fingers = detector.fingersUp()

        # Move Mouse (Index finger Up)
        if fingers[1] == 1 and fingers[2] == 0:
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

        # Volume Control (Thumb Up/Down)
        if fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            if y_thumb < y_index_base - 20:  
                pyautogui.press("volumeup")
                time.sleep(0.2)
            elif y_thumb > y_index_base + 20:  
                pyautogui.press("volumedown")
                time.sleep(0.2)

        # Scrolling Up & Down (Now Fixed)
        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            # Measure distance between fingers (index-middle & ring-pinky)
            distance_12_16 = np.hypot(lmList[12][0] - lmList[16][0], lmList[12][1] - lmList[16][1])  
            distance_16_20 = np.hypot(lmList[16][0] - lmList[20][0], lmList[16][1] - lmList[20][1])

            if distance_12_16 < CLOSE_DISTANCE and distance_16_20 < CLOSE_DISTANCE:
                pyautogui.scroll(SCROLL_SPEED)  # Scroll up
            elif distance_12_16 > OPEN_DISTANCE and distance_16_20 > OPEN_DISTANCE:
                pyautogui.scroll(-SCROLL_SPEED)  # Scroll down

    # Display the video feed
    cv2.imshow("Virtual Mouse", img)
    cv2.waitKey(1)
