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
        t2 = threading.Thread(target = self.head_cam)
        t2.start()
        t3 = threading.Thread(target = self.parking_algo)
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
            #print(len(self.pole_cnts))
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
            self.dir = rec.park_dir(frame, self.center)
            
        cap.release()
        cv2.destroyAllWindows()

    def parking_algo(self):
        self.state = 5
        prev_state = 0
        while True:

            if self.state == 1:
                self.search()
                self.state = self.state + 1
            elif self.state == 2:
                self.align()
                if prev_state == 4:
                    prev_state = 2
                    self.state = 4
                else:
                    self.state = self.state + 1
            elif self.state == 3:
                self.forward()
                self.state = self.state + 1
            elif self.state == 4:
                self.corr_entry()
                if prev_state == 4:
                    self.state = 2
                else:
                    print("End state 4!!!!!!!")
                    ser.write('p'.encode())
                    time.sleep(3)
                    self.state = self.state + 1
            elif self.state == 5:
                time.sleep(3)
                self.park()
                self.state = 7
                #self.state = self.state + 1
            elif self.state == 6:
                self.park_adjust()
                self.state = self.state + 1
                
    def search(self):
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
        time.sleep(1)
        print("end state 1")
    
    def align(self):
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
        time.sleep(1)
    
    def forward(self):
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
        time.sleep(1)

    def corr_entry(self):
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

    def park(self):
        print("Forward")
        ser.write('d'.encode())
        while True:
            try:
                center = self.center
                if center != (0,0):
                    print(center)
                    break
            except:
                pass

        print("Arrived.")
        ser.write('p'.encode())
        time.sleep(1)
    
    def park_adjust(self):
        print("Going Forward")
        while True:
            try:
                nav = []
                x_diff = self.dir[0]
                y_diff = self.dir[1]
                if x_diff < 0:
                    print("Go forward")
                    ser.write('d'.encode())
                    time.sleep(0.2)
                elif x_diff > 0:
                    print("Go backward")
                    ser.write('e'.encode())
                    time.sleep(0.2)
                if y_diff < 0:
                    print("Go left")
                    ser.write('a'.encode())
                    time.sleep(0.2)
                elif y_diff > 0:
                    print("Go right")
                    ser.write('b'.encode())
                    time.sleep(0.2)
                
                print(x_diff, y_diff)

            except:
                pass

        print("Arrive at target.")
        ser.write('p'.encode())


thread = myThread()