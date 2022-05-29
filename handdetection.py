from ast import Dict
from this import d
import cv2
import mediapipe as mp
import time
import os
import copy

class handDetector():
    def __init__(self, mode = False, maxHands = 2, detectionCon=0.5, trackCon =0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, min_detection_confidence = self.detectionCon, min_tracking_confidence = self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw = True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        """ if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms) # self.mpHands.HAND_CONNECTIONS  
        return img"""
        

    def findPosition(self, img, handNo):
        self.findHands(img)
        if self.results.multi_hand_landmarks:
            Hands = self.results.multi_hand_landmarks #[handNo]
            dic = dict()
            i = 0
            for myHand in Hands:
                lmList = []
                for id, lm in enumerate(myHand.landmark):
                    """ if id == 8 or id == 5: #To choose which point to focus """
                    h, w, c = img.shape
                    cx, cy = int(lm.x*w), int(lm.y*h)
                    lmList.append([id, cx, cy])
                    """ if draw and id==8:
                        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED) """
                dic[i] = lmList
                if i >= handNo-1:
                    break
                i+=1
            return dic
        return False

def getHandPos(lmList, key):
    new_hand = list()
    if lmList[key][5][2]>lmList[key][8][2]:
        new_hand.append(1)
    else:
        new_hand.append(0)
                
    if lmList[key][9][2]>lmList[key][12][2]:
        new_hand.append(1)
    else:
        new_hand.append(0)
    return new_hand

def changeColor(lmList, key, img):
    #Change colors if index and middle fingers up
    poscolor = [lmList[key][8][1], lmList[key][8][2]-10]
    if poscolor == None:
        return
    color = [int(img[poscolor[1], poscolor[0]][0]), int(img[poscolor[1], poscolor[0]][1]), int(img[poscolor[1], poscolor[0]][2])]
    cv2.circle(img, (poscolor[0], poscolor[1]), 8, color, cv2.FILLED)
    return color

def updateHands(hands, lmList, key, handsmemory):
    new_hand = getHandPos(lmList, key)
    if key in hands:
        hands[key] = hands[key] + [new_hand]
    else:
        hands[key] = [new_hand]
    while len(hands[key])-1 > handsmemory: #Remove old hands
            hands[key].pop(0) 
    return hands

def checkConds(hands, key):
    d_cond = list()
    c_cond = list()
    s_cond = list()
    for i in range(len(hands[key])-1, 0, -1):
        if hands[key][i][0] == 1:
            d_cond.append(1)
            s_cond.append(0)
            if hands[key][i][1] == 1:
                c_cond.append(1)
            else:
                c_cond.append(0)
        else:
            d_cond.append(0)
            c_cond.append(0)
        if hands[key][i][0] == 0 and hands[key][i][1] == 0:
            s_cond.append(1)
    return d_cond, c_cond, s_cond

def newDraw(d_cond):
    if 1 in d_cond:
        d_cond_neg = copy.copy(d_cond)
        try:
            while True:
                d_cond_neg.remove(1)
        except ValueError:
            pass
        if len(d_cond_neg)<=len(d_cond)//2:
            #Draw if the index is up in the majority of the cases
            draw = True   
        else:
            #Don't draw if the index is down in the majority of the cases
            draw = False
        return draw
    return False
    

def newColor(c_cond, lmList, key, img, color):
    if 1 in c_cond:
        c_cond_neg = copy.copy(c_cond)
        try:
            while True:
                c_cond_neg.remove(1)
        except ValueError:
            pass
        if len(c_cond_neg)<=len(c_cond)//2:
            color = changeColor(lmList, key, img)
    return color

def stop(s_cond):
    if 1 in s_cond:
        s_cond_neg = copy.copy(s_cond)
        try:
            while True:
                s_cond_neg.remove(1)
        except ValueError:
            pass
        if len(s_cond_neg)<=len(s_cond)//2:
            #Stop if the index and middle are down in the majority of the cases
            stop = True   
        else:
            #Don't stop if the index and middle are up in the majority of the cases
            stop = False
        return stop
    return False

def addLines(lmList, coords, maxlines):
    for key in lmList:
        if key in coords:
            #Add coords to previous ones
            coords[key] = coords[key] + [lmList[key][8][1:]]
        else:
            #First time using coords
            coords[key] = [lmList[key][8][1:]]
        while len(coords[key]) >= maxlines: #Remove old lines
            coords[key].pop(0)
    return coords

def drawLines(coords, img, color, linewidth, maxlines):
    for key in coords:
        pcoord = 0
        alpha = 1
        for coord in coords[key]:
            if pcoord != 0 and pcoord != coord: 
                new_img = img.copy()
                cv2.line(new_img, pcoord, coord, color, linewidth)
                img = cv2.addWeighted(new_img, 1-alpha, img, alpha, 0)
            pcoord = coord
            alpha -= 1/(maxlines-1)
    return img

def main():
    handNo = 2
    draw = True
    color = [255, 0, 255]
    linewidth= 5
    maxlines = 40
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    coords = dict()
    hands = dict()
    handsmemory = 20

    while True:
        _, img = cap.read()
        lmList = detector.findPosition(img, handNo)
        if lmList != False:
            for key in lmList:
                hands = updateHands(hands, lmList, key, handsmemory)
                d_cond, c_cond, s_cond = checkConds(hands, key)
                draw = newDraw(d_cond)
                color = newColor(c_cond, lmList, key, img, color)
                end = stop(s_cond)   
            if end:
                print("Hand closed on the screen: End of drawing session")
                quit()
            if draw:
                coords = addLines(lmList, coords, maxlines)

        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        img = drawLines(coords, img, color, linewidth, maxlines)

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255),  3) 

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()