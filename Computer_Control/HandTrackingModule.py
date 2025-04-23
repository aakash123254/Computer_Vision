import cv2
import mediapipe as mp
import time

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


class HandDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode, self.maxHands, 1, self.detectionCon, self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 8, (255, 0, 255), cv2.FILLED)
        return lmList

    def fingersUp(self):
        fingers=[]
        tipIds = [4,8,12,16,20]
        
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[0]
            
            #Thumb 
            if myHand.landmark[tipIds[0]].x < myHand.landmark[tipIds[0]-1].x:
                fingers.append(1)
            else:
                fingers.append(0)
            
            #4 Fingers 
            for id in range(1,5):
                if myHand.landmark[tipIds[id]].y < myHand.landmark[tipIds[id]-2].y:
                    fingers.append(1)
                else:
                    fingers.append(0)
        return fingers