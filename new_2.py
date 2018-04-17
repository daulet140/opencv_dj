# -*- coding: utf-8 -*-
##Подсчет людей
##Ryssaly Assylzhan
import numpy as np
import cv2
import Person
import time
from db import jdbc as db

# Входы и выходы
cnt_up = 0
cnt_down = 0

# Источник видео
cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('rtsp://192.168.1.199/Streaming/Channels/101')

# Свойства видео
##cap.set(3,160) #Width
##cap.set(4,120) #Height

# Печать свойств захвата на консоль
for i in range(19):
    print ((i, cap.get(i)))

w = cap.get(3)
h = cap.get(4)
frameArea = h * w
areaTH = frameArea / 250
print (('Area Threshold', areaTH))

# Линии входа / выхода
line_up = int(2 * (h / 5))
line_down = int(3 * (h / 5))

up_limit = int(1 * (h / 5))
down_limit = int(4 * (h / 5))

print (("Red line y:", str(line_down)))
print (("Blue line y:", str(line_up)))
line_down_color = (0, 0, 255)
line_up_color = (0, 255, 255)
pt1 = [0, line_down];
pt2 = [w, line_down];
pts_L1 = np.array([pt1, pt2], np.int32)
pts_L1 = pts_L1.reshape((-1, 1, 2))
pt3 = [0, line_up];
pt4 = [w, line_up];
pts_L2 = np.array([pt3, pt4], np.int32)
pts_L2 = pts_L2.reshape((-1, 1, 2))

pt5 = [0, up_limit];
pt6 = [w, up_limit];
pts_L3 = np.array([pt5, pt6], np.int32)
pts_L3 = pts_L3.reshape((-1, 1, 2))
pt7 = [0, down_limit];
pt8 = [w, down_limit];
pts_L4 = np.array([pt7, pt8], np.int32)
pts_L4 = pts_L4.reshape((-1, 1, 2))

# Фон субтрактора
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

# Структурирующие элементы для морфографических фильтров
kernelOp = np.ones((3, 3), np.uint8)
kernelOp2 = np.ones((5, 5), np.uint8)
kernelCl = np.ones((11, 11), np.uint8)

# Переменные
font = cv2.FONT_HERSHEY_SIMPLEX
persons = []
max_p_age = 5
pid = 1

while (cap.isOpened()):
    ##for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # Прочитать изображение источника видео
    ret, frame = cap.read()
    ##    frame = image.array

    for i in persons:
        i.age_one()  # age every person one frame
    #########################
    #   ПРЕДВАРИТЕЛЬНАЯ ОБРАБОТКА   #
    #########################

    # Применить вычитание фона
    fgmask = fgbg.apply(frame)
    fgmask2 = fgbg.apply(frame)

    # Binariazcion для устранения теней (color gris)
    try:
        ret, imBin = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
        ret, imBin2 = cv2.threshold(fgmask2, 200, 255, cv2.THRESH_BINARY)
        # Открытие (размывание-> расширение) для удаления шума.
        mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernelOp)
        mask2 = cv2.morphologyEx(imBin2, cv2.MORPH_OPEN, kernelOp)
        # Закрытие (расширение -> эрозия) для соединения белых областей.
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernelCl)
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernelCl)
    except:
        print('EOF')
        print ('ВВЕРХ:', cnt_up)
        print ('ВНИЗ:', cnt_down)
        break

    ##  КОНТУР   ##

    # RETR_EXTERNAL returns only extreme outer flags. All child contours are left behind.
    _, contours0, hierarchy = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours0:
        area = cv2.contourArea(cnt)
        if area > areaTH:
            ##   TRACKING    ##
            # Отсутствующие условия для мультиперсонажей, выходов и записей экрана.
            M = cv2.moments(cnt)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            x, y, w, h = cv2.boundingRect(cnt)

            new = True
            if cy in range(up_limit, down_limit):
                for i in persons:
                    if abs(cx - i.getX()) <= w and abs(cy - i.getY()) <= h:
                        # объект близок к тому, который уже был обнаружен до
                        new = False
                        i.updateCoords(cx, cy)  # обновлять координаты в объекте и сбрасывать возраст
                        if i.going_UP(line_down, line_up) == True:
                            cnt_up += 1;
                            print ("ID:", i.getId(), 'crossed going up at', time.strftime("%c"))
                        elif i.going_DOWN(line_down, line_up) == True:
                            cnt_down += 1;
                            print ("ID:", i.getId(), 'crossed going down at', time.strftime("%c"))
                        break
                    if i.getState() == '1':
                        if i.getDir() == 'down' and i.getY() > down_limit:
                            i.setDone()
                        elif i.getDir() == 'up' and i.getY() < up_limit:
                            i.setDone()
                    if i.timedOut():
                        # удалить людей из списка
                        index = persons.index(i)
                        persons.pop(index)
                        del i  # освободить память для i
                if new == True:
                    p = Person.MyPerson(pid, cx, cy, max_p_age)
                    db.insert2Table(p)
                    persons.append(p)
                    pid += 1

            ##   ЧЕРТЕЖИ     ##

            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            img = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # cv2.drawContours(frame, cnt, -1, (0,255,0), 3)

    # END for cnt in contours0

    ## ТРАЕКТОРИИ ЧЕРТЕЖЕЙ  ##

    for i in persons:
        ##        if len(i.getTracks()) >= 2:
        ##            pts = np.array(i.getTracks(), np.int32)
        ##            pts = pts.reshape((-1,1,2))
        ##            frame = cv2.polylines(frame,[pts],False,i.getRGB())
        ##        if i.getId() == 9:
        ##            print str(i.getX()), ',', str(i.getY())
        cv2.putText(frame, str(i.getId()), (i.getX(), i.getY()), font, 0.3, i.getRGB(), 1, cv2.LINE_AA)

    ## ИЗОБРАЖЕНИЯ   ##

    str_up = 'going_UP: ' + str(cnt_up)
    str_down = 'going_DOWN: ' + str(cnt_down)
    str_emb = 'ASSYLZHAN RYSSALY'
    frame = cv2.polylines(frame, [pts_L1], False, line_down_color, thickness=2)
    frame = cv2.polylines(frame, [pts_L2], False, line_up_color, thickness=2)
    frame = cv2.polylines(frame, [pts_L3], False, (255, 255, 255), thickness=1)
    frame = cv2.polylines(frame, [pts_L4], False, (255, 255, 255), thickness=1)
    cv2.putText(frame, str_up, (10, 90), font, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, str_up, (10, 90), font, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, str_down, (10, 400), font, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, str_down, (10, 400), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, str_emb, (220, 20), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, str_emb, (220, 20), font, 0.7, (255, 0, 0), 1, cv2.LINE_AA)

    cv2.imshow('Frame', frame)
    # cv2.imshow('Mask',mask)

    # Предварительно нажмите ESC для выхода
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
# END while(cap.isOpened())


#  ОЧИСТКА    #

cap.release()
cv2.destroyAllWindows()
