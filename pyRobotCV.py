import cv2
import time
import numpy as np

capture = cv2.VideoCapture(0)
# filter for green objects 101 145 131 255 255 255
##rangeMin = np.array([131,16,0],np.uint8)
##rangeMax = np.array([255,255,255],np.uint8)

# filter for red objects
rangeMin = np.array([136, 87, 111], np.uint8)
rangeMax = np.array([180, 255, 255], np.uint8)


def Forward():
    # Motor 1
    gpio.output(13, True)
    gpio.output(15, False)
    # Motor 2
    gpio.output(18, False)
    gpio.output(22, True)
    print('Stop')
    print('Forward')


def Backward():
    # Motor 1
    gpio.output(13, False)
    gpio.output(15, True)
    # Motor 2
    gpio.output(18, True)
    gpio.output(22, False)
    print('Backward')


def Stop():
    # Motor 1
    gpio.output(13, False)
    gpio.output(15, False)
    # Motor 2
    gpio.output(18, False)
    gpio.output(22, False)
    print('Stop')


def Left():
    # Motor 1
    gpio.output(13, True)
    gpio.output(15, False)
    # Motor 2
    gpio.output(18, True)
    gpio.output(22, False)


def Right():
    # Motor 1
    gpio.output(13, False)
    gpio.output(15, True)
    # Motor 2
    gpio.output(18, False)
    gpio.output(22, True)


def processamento(entrada):
    imgMedian = cv2.medianBlur(entrada, 1)
    # imgHSV = cv2.cvtColor(imgMedian, cv2.COLOR_BGR2HSV )
    imgHSV = cv2.cvtColor(imgMedian, cv2.COLOR_BGR2HSV)
    imgThresh = cv2.inRange(imgHSV, rangeMin, rangeMax)
    imgErode = cv2.erode(imgThresh, None, iterations=3)
    return imgErode


# ------------------------------------------------- ----------------------
# REGULATED SAMPLES
# ------------------------------------------------- ----------------------
# Captured image size options
largura = 300
altura = 300

# Minimum detection area#
minArea = 100  # about 80cm

# Axis center
centroy = largura / 2

# center constraint
may = altura / 5  # 24
# ----------------------------------------------------------------------

# d=(altura-may)

#   Set size for frames (discarding Pyramid Down)
if capture.isOpened():
    capture.set(3, largura)  # capture.set(3,largura)
    capture.set(4, altura)  # capture.set(4,altura)

while True:
    ret, entrada = capture.read()
    imagem_processada = processamento(entrada)
    moments = cv2.moments(imagem_processada, True)
    area = moments['m00']

    se = np.ones((7, 7), dtype='uint8')
    image_close = cv2.morphologyEx(imagem_processada, cv2.MORPH_CLOSE, se)
    cnts = cv2.findContours(image_close, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]

    for (i, c) in enumerate(cnts):
        # draw the contour
        ((x, y), _) = cv2.minEnclosingCircle(c)
        cv2.putText(entrada, "#{}".format(i + 1), (int(x) - 10, int(y)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.drawContours(entrada, [c], -1, (0, 255, 0), 2)
        cv2.putText(entrada, "Object {}".format(i + 1), (0, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    #    cv2.line(entrada,(70,0),(70,300),(255,0,0),5) # left line
    #    cv2.line(entrada,(230,0),(230,300),(255,0,0),5) #right line
    #    cv2.rectangle(entrada, (70,70), (230,180), (0,0,255), thickness=2, lineType=8, shift=0) #central square
    #    cv2.line(entrada,(0,30),(320,30),(255,0,255),5) #top line
    #    cv2.line(entrada,(0,210),(320,210),(255,0,255),5) #bottom line

    if moments['m00'] >= minArea:
        x = moments['m10'] / moments['m00']
        y = moments['m01'] / moments['m00']
        cv2.circle(entrada, (int(x), int(y)), 5, (0, 255, 0), -1)

        if x >= 70 and x <= 230:
            if y >= 70 and y <= 180:
                if (area <= 500):
                    Forward()
                    cv2.putText(entrada, "The object is far", (0, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                elif (area >= 1000):
                    Stop()
                    cv2.putText(entrada, "The object is close", (0, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                # Если предел больше, чем расстояние от центра, которое считается централизованным

        if x >= 0 and x <= 70:
            Left()
            cv2.putText(entrada, "Left", (0, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            print('left')

        elif x >= 230 and x <= 300:
            Right()
            cv2.putText(entrada, "Right", (0, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            print('right')
        if y >= 0 and y <= 70:
            Forward()
            cv2.putText(entrada, "Up", (0, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            print('up')

        elif y >= 210 and y <= 300:
            Backward()
            cv2.putText(entrada, "Down", (0, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            print('down')

    cv2.imshow("Entrada", entrada)
    # cv2.imshow("HSV", imgHSV)
    # cv2.imshow("Thre", imgThresh)
    cv2.imshow("Erosao", imagem_processada)

    if cv2.waitKey(10) == 27:  # if cv2.waitKey(10) == 27
        break
        cv.DestroyAllWindows()
        gpio.cleanup()
