import cv2
import time
import numpy as np
from PIL import Image
from key import Button
from xgolib import XGO
import threading
import xgoscreen.LCD_2inch as LCD_2inch

import face_recognition

exit_mark = False
acting = False
x = y = r = 0

dog = XGO(port='/dev/ttyAMA0', version="xgolite")
fm = dog.read_firmware()

if fm[0] == 'M':
    print('XGO-MINI')
    dog = XGO(port='/dev/ttyAMA0', version="xgomini")
    dog_type = 'M'
else:
    print('XGO-LITE')
    dog_type = 'L'

display = LCD_2inch.LCD_2inch()
display.clear()
splash = Image.new("RGB", (display.height, display.width), "black")
display.ShowImage(splash)

button = Button()
width, height = 320, 240
camera = cv2.VideoCapture(0)
camera.set(3, width)
camera.set(4, height)


def move_thread(speed, action_time, turn_time, reset_time, attitude_value, translation_value):
    global x, y, r, acting, exit_mark
    while not exit_mark:
        if acting:
            time.sleep(action_time)
            dog.claw(0)
            time.sleep(reset_time)
            dog.reset()
            time.sleep(reset_time)
            dog.attitude('p', attitude_value)
            time.sleep(reset_time)
            dog.translation('z', translation_value)
            acting = False
        else:
            if r > 48:
                Back(5)
            elif 43 <= r < 48:
                acting = True
                dog.action(130)
            else:
                if x == 0:
                    Stop()
                elif x < 135:
                    Left(speed)
                elif x > 185:
                    Right(speed)
                else:
                    if 10 < r < 25:
                        Front(35, 0.9)
                    elif r < 34:
                        Front(10, 0.8)


def Front(speed, time_interval):
    global acting
    acting = True
    dog.move('x', speed)
    time.sleep(time_interval)
    dog.stop()
    time.sleep(0.1)
    acting = False


def Back(speed):
    global acting
    acting = True
    dog.move('x', 0 - speed)
    time.sleep(0.7)
    dog.stop()
    time.sleep(0.1)
    acting = False


def Left(speed):
    global acting
    acting = True
    dog.turn(speed)
    time.sleep(1.1)
    dog.stop()
    time.sleep(0.2)
    acting = False


def Right(speed):
    global acting
    acting = True
    dog.turn(0 - speed)
    time.sleep(1.1)
    dog.stop()
    time.sleep(0.2)
    acting = False


def Stop():
    global acting
    if not acting:
        dog.turn(0)
        dog.move('x', 0)


def Image_Processing():
    global x, y, r, acting
    ret, frame = camera.read()
    image = frame
    x = y = r = 0
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = cv2.medianBlur(gray_img, 5)
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 20, param1=100, param2=35, minRadius=10, maxRadius=66)
    if not acting:
        if circles is not None:
            x, y, r = int(circles[0][0][0]), int(circles[0][0][1]), int(circles[0][0][2])
            cv2.circle(image, (x, y), r, (255, 0, 255), 5)
        else:
            (x, y), r = (0, 0), 0
    b, g, r1 = cv2.split(image)
    image = cv2.merge((r1, g, b))
    image = cv2.flip(image, 1)
    imgok = Image.fromarray(image)
    display.ShowImage(imgok)
    if x != 0 and y != 0 and r != 0:
        print(x, y, r)



def main_thread():
    global exit_mark
    while True:
        Image_Processing()
        if button.press_b():
            dog.reset()
            exit_mark = True
            break
        if button.press_a():
            dog.reset()
            dog.action(130)


if dog_type == 'L':
    move_thread = threading.Thread(target=move_thread, args=(10, 10, 1, 1, 99, 70))
elif dog_type == 'M':
    move_thread = threading.Thread(target=move_thread, args=(9, 10, 1, 1, 100, 100))
move_thread.start()

main_thread()
move_thread.join()
