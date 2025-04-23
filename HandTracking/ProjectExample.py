import cv2
import mediapipe as mp
import time
import HandTrackingModule as htm

pTime = 0
cap = cv2.VideoCapture(0)  # Change to 1 if using an external camera

if not cap.isOpened():
    print("Error: Could not access webcam")
    exit()

detector = htm.handDetector()

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        continue  # Skip this frame and try again

    img = detector.findHands(img, draw=True)
    lmList = detector.findPosition(img, draw=False)

    if lmList:
        print("Index Finger Tip:", lmList[4])

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == 27:  # Press 'ESC' to exit
        break

cap.release()
cv2.destroyAllWindows()
