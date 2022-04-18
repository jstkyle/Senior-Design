import cv2
import recognition as rec
import time
import serial
import numpy as np
import threading


ser = serial.Serial(            
    port='/dev/serial0',
    baudrate = 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

class myThread(threading.Thread):

    def __init__(self):

        t1 = threading.Thread(target = self.front_cam)
        t1.start()
        t2 = threading.Thread(target = self.parking_algo)
        t2.start()
        t3 = threading.Thread(target = self.head_cam)
        t3.start()


    def front_cam(self):

        # Start camera
        cap = cv2.VideoCapture(0)
        # Check if the webcam is opened correctly
        if not cap.isOpened():
            raise IOError("Cannot open webcam")
        
        while True:
            ret, frame = cap.read()

            if frame is None:
                print("No frame")
                break

            blur = cv2.GaussianBlur(frame, (5,5), 0)
            self.midpoints, self.pole_cnts = rec.detect_poles(blur, frame)
            print(len(self.pole_cnts))
            self.dist = rec.dist(frame, self.pole_cnts)
            self.side = rec.detect_side(self.pole_cnts)
            self.entry = rec.is_entry(self.pole_cnts)
            midpoint = rec.steer(self.midpoints)
            self.target = rec.dash(frame, midpoint)
            
        cap.release()
        cv2.destroyAllWindows()

    def head_cam(self):

        # Start camera
        cap = cv2.VideoCapture(2)
        # Check if the webcam is opened correctly
        if not cap.isOpened():
            raise IOError("Cannot open webcam")
        
        while True:
            ret, frame = cap.read()

            if frame is None:
                print("No frame")
                break

            blur = cv2.GaussianBlur(frame, (5,5), 0)
            self.center = rec.detect_circle(blur)
            
        cap.release()
        cv2.destroyAllWindows()

    def parking_algo(self):
        state = 1
        prev_state = 0
        while True:

            if state == 1:
                print("start spinning")
                ser.write('r'.encode())
                
                while True:
                    try:
                        poles = self.pole_cnts
                        if len(poles) > 1:
                            break
                    except:
                        pass

                print("Found Target!!!!!!!")
                ser.write('p'.encode())
                time.sleep(3)
                print("end state 1")
                state = state + 1
            elif state == 2:
                print("Align with midpoint")
                while True:
                    try:
                        target = self.target
                        print(target)
                        if target > 3:
                            ser.write('t'.encode())
                            time.sleep(0.05)
                            ser.write('p'.encode())
                        elif target < -3:
                            ser.write('g'.encode())
                            time.sleep(0.05)
                            ser.write('p'.encode())
                        else:
                            break
                    except:
                        pass
                print("Aligned with midpoint!!!!!!!")
                ser.write('p'.encode())
                time.sleep(3)
                if prev_state == 4:
                    prev_state = 2
                    state = 4
                else:
                    state = state + 1
            elif state == 3:
                print("Going Forward")
                ser.write('o'.encode())
                while True:
                    try:
                        dist = self.dist
                        #print(dist)
                        if dist <= 90:
                            break
                    except:
                        pass

                print("Arrive at target.")
                ser.write('p'.encode())
                time.sleep(3)
                state = state + 1
            elif state == 4:
                print("Aligning...")
                while True:
                    try:
                        side = self.side
                        entry = self.entry
                        #print(side)
                        if entry is True:
                            break
                        elif side == "left":
                            print("slide right")
                            ser.write('b'.encode()) # move right
                            time.sleep(0.2)
                            ser.write('p'.encode())
                            prev_state = 4
                            break
                        elif side == "right":
                            print("slide left")
                            ser.write('a'.encode()) # move left
                            time.sleep(0.2)
                            ser.write('p'.encode())
                            prev_state = 4
                            break
                    except:
                        pass

                if prev_state == 4:
                    state = 2
                else:
                    print("End state 4!!!!!!!")
                    ser.write('p'.encode())
                    time.sleep(3)
                    state = state + 1
            elif state == 5:
                print("Forward")
                ser.write('l'.encode())
                while True:
                    try:
                        gap = self.gap
                        print(gap)
                        if gap is True:
                            break
                    except:
                        pass

                print("Correct entry point.")
                ser.write('p'.encode())
                time.sleep(3)
                state = state + 1
            elif state == 6:
                print("Going Forward")
                ser.write('o'.encode())
                while True:
                    try:
                        dist = self.dist
                        print(dist)
                        if dist <= 70:
                            break
                    except:
                        pass

                print("Arrive at target.")
                ser.write('p'.encode())
                state = state + 1
                




thread = myThread()