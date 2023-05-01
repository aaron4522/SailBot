"""
Testing scripts for 
"""
import keyboard

import constants as c
from camera import Camera

def manual_test_camera(cam):
    """Manually test camera capture, servo movement and object detection
    Controls:
        - Arrow Keys (servo movement)
        - Enter (Take a picture)
    """
    while True:
        print(f"Pitch: {cam.servos.pitch} Yaw: {cam.servos.yaw}\n")
        if keyboard.is_pressed("enter"):
            cam.capture(context=False, show=True)
        elif keyboard.is_pressed("space"):
            cam.servos.reset()
        elif keyboard.is_pressed("up arrow"):
            cam.servos.pitch = cam.servos.pitch + 1
        elif keyboard.is_pressed("down arrow"):
            cam.servos.pitch = cam.servos.pitch - 1
        elif keyboard.is_pressed("left arrow"):
            cam.servos.yaw = cam.servos.yaw - 1
        elif keyboard.is_pressed("right arrow"):
            cam.servos.yaw = cam.servos.yaw + 1
        


if __name__ == "__main__":
    cam = Camera()
    while True:
        print('''
=============================
Accepted Command info:
[0] freemove(): free control movement wise with continuous capture feed for demonstration purposes
[1] survey(): go far left,right,center looking for buoy whole time detect() - 3 set points in x axis
[2] track(): follow object
-----------------------------''')
        inp = input("Command Test: ")
        
        if inp == "0":
            cam.freemove()
        if inp == "1":
            cam.survey()
        else:
            print("nah...")
            raise Exception("invalid command selection")
