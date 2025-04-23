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
SCROLL_SPEED = 100  
SCROLL_DOWN_SPEED = -100  
CLOSE_DISTANCE = 30  
OPEN_DISTANCE = 100  

# Exit gesture variables
exit_start_time = None  
EXIT_HOLD_TIME = 2  

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
        # Get coordinates of index and middle fingers
        x1, y1 = lmList[8][1], lmList[8][2]  # Index finger tip
        x2, y2 = lmList[12][1], lmList[12][2]  # Middle finger tip
        x_thumb, y_thumb = lmList[4][1], lmList[4][2]  # Thumb tip
        y_index_base = lmList[5][2]  # Base of index finger (for volume detection)

        # Find which fingers are up
        fingers = detector.fingersUp()

        # Move Mouse (Index finger Up)
        if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            screen_x = np.interp(x1, (MARGIN_X, wCam - MARGIN_X), (screen_w, 0))  
            screen_y = np.interp(y1, (MARGIN_Y, hCam - MARGIN_Y), (0, screen_h))  

            # Smooth cursor movement
            curr_x = prev_x + (screen_x - prev_x) / smoothening
            curr_y = prev_y + (screen_y - prev_y) / smoothening

            # Move the mouse cursor
            pyautogui.moveTo(curr_x, curr_y)

            prev_x, prev_y = curr_x, curr_y

        # Click the Mouse (Index and middle finger up, fingers apart)
        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            distance = np.hypot(x2 - x1, y2 - y1)  # Distance between index and middle finger
            if distance > 40:  # Only click if fingers are apart (not making "X")
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

        # ✅ Perfectly Fixed Scroll Up & Down
        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            distance_12_16 = np.hypot(lmList[12][0] - lmList[16][0], lmList[12][1] - lmList[16][1])  
            distance_16_20 = np.hypot(lmList[16][0] - lmList[20][0], lmList[16][1] - lmList[20][1])

            if distance_12_16 < CLOSE_DISTANCE and distance_16_20 < CLOSE_DISTANCE:
                pyautogui.scroll(SCROLL_SPEED)  # ✅ Scroll up smoothly
            elif distance_12_16 > OPEN_DISTANCE and distance_16_20 > OPEN_DISTANCE:
                pyautogui.hscroll(SCROLL_DOWN_SPEED)  # ✅ Fixed smooth scroll down (No more line selection)

        # ✖️ Exit System ("X" Gesture) - Now Fully Fixed
        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            distance_x = abs(x1 - x2)  # Distance between index and middle finger horizontally
            distance_y = abs(y1 - y2)  # Distance vertically

            index_is_left = x1 < x2
            middle_is_left = x2 < x1

            if distance_x < 40 and distance_y < 40 and index_is_left != middle_is_left:
                if exit_start_time is None:  
                    exit_start_time = time.time()  # Start timer
                elif time.time() - exit_start_time > EXIT_HOLD_TIME:  # Hold for 2 seconds
                    print("Exit Gesture Detected! Closing...")
                    break  # Exit the program
            else:
                exit_start_time = None  # Reset timer if gesture breaks

    # Display the video feed
    cv2.imshow("Virtual Mouse", img)
    cv2.waitKey(1)

# Release the webcam
cap.release()
cv2.destroyAllWindows()
