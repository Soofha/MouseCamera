import time

import cv2
import mediapipe as mp
import pyautogui as pag

MODE = False
MAX_HANDS = 2
DETECTION_CON = 0.5
TRACK_CON = 0.5
HANDS_FUNCTION = mp.solutions.hands.Hands(MODE, MAX_HANDS, DETECTION_CON, TRACK_CON)
MP_DRAW = mp.solutions.drawing_utils
positionsFingerTip = []
def findHands(img):
    
        return HANDS_FUNCTION.process(img)


def drawHands(hands, img):
    if hands.multi_hand_landmarks:
            for handLms in hands.multi_hand_landmarks:
                    MP_DRAW.draw_landmarks(img, handLms, mp.solutions.hands.HAND_CONNECTIONS)

def findPositionHand(hands, w, h, handNumber = 0):
        lmlist = []
        if hands.multi_hand_landmarks:
            for id, lm in enumerate(hands.multi_hand_landmarks[handNumber].landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmlist.append([id, cx, cy])
        return lmlist
'''
return value [X, Y]
X=-1 right
X=1 left
Y=-1 top
Y=1 bottom
'''        
def chekingPosition(position, fps=6):
    #TODO перепроверить корректность значений
    returnValue = [0,0]
    if(len(positionsFingerTip)>=fps):
        if len(positionsFingerTip)>0:
            del positionsFingerTip[0]
    else:
        positionsFingerTip.append(position)
        return returnValue
    positionsFingerTip.append(position)
    top = True
    bottom = True
    right = True
    left = True
    lastY = positionsFingerTip[0][2]
    lastX = positionsFingerTip[0][1]
    
    for pos in positionsFingerTip[1::]:
        if(pos[2]>lastY):
            top=False
        else:
            bottom=False
        lastY= pos[2]
        if(pos[1]>lastX):
            right =False
        else:
           left =False
        lastX= pos[1]
    if top:
        returnValue[1]=1
    if bottom:
        returnValue[1]=-1
    if left:
        returnValue[0]=1
    if right:
        returnValue[0]=-1
    return returnValue

def clearPosition():
    positionsFingerTip.clear

flagClick = True
def chekingClick(positions):
    #Индексы для безымянного пальца:16 15 14 13
    global flagClick
    if positions[16][2]>positions[13][2] and positions[15][2]>positions[13][2] and positions[14][2]<positions[13][2] :
        if flagClick == False:
            return
        flagClick=False
    else:
        flagClick=True

pTime =0
cTime =0
def fpsCounter():
    global pTime
    global cTime
    cTime = time.time()
    fps = int(1 / (cTime - pTime))
    pTime = cTime
    return fps

def main():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        success, img = cap.read()
        fps = fpsCounter()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        hands = findHands(img)
        lmlist = []
        if hands.multi_hand_landmarks:
            w, h = pag.size()
            lmlist = findPositionHand(hands, w,h)
            #TODO доделать перескоки за пределы экрана
            pag.moveTo(w-lmlist[8][1], lmlist[8][2])
            if lmlist[16][2]>lmlist[13][2] and lmlist[15][2]>lmlist[13][2] and lmlist[14][2]<lmlist[13][2] :
                if flagClick == True:
                    flagClick=False
                    pag.click()
            else:
                flagClick=True
        cv2.putText(img, str(fps), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        
        cv2.imshow("Image", img)
        # TODO При считывании любых клавиш происходит: "Ошибка сегментирования (стек памяти сброшен на диск)"
        # Проблема возникает из-за одновременного импорта opencv и mediapipe
        if 27==cv2.waitKey(1):
            break
if __name__ == "__main__":
    main()