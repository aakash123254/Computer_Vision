import cv2
import time 
import HandTrackingModule as htm 

cap = cv2.VideoCapture(0)
detector = htm.HandDetector()

pTime=0

while True:
    success,img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw=True)
    
    if len(lmList)!=0:
        print(lmList[4])
    
    #FPS Calculation 
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, f'FPS:{int(fps)}',(10,70),cv2.FONT_HERSHEY_PLAIN,3,(255,0,255),3)
    
    cv2.imshow("Hand Tracking Test",img)
    cv2.waitKey(1)
    