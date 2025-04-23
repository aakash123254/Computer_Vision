import cv2
import mediapipe as mp
import time

# Initialize video capture (Use 0 for built-in webcam, 1 for external)
cap = cv2.VideoCapture(0)  # Change to 1 if external webcam

if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

# Initialize Mediapipe Hands module
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

pTime = 0

while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame")
        continue  # Skip processing if frame not captured properly

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                print(f"ID: {id}, X: {cx}, Y: {cy}")

                # Draw circle on each landmark
                cv2.circle(img, (cx, cy), 8, (255, 0, 255), cv2.FILLED)

            # Draw hand connections
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    # Calculate FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # Display FPS on screen
    cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)

    # Show image
    cv2.imshow("Hand Tracking", img)

    # Exit when 'ESC' key is pressed
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
