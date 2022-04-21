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

        self.cam1 = True
        self.t1 = threading.Thread(target = self.front_cam)
        self.t1.start()
        self.t2 = threading.Thread(target = self.head_cam)
        
        t3 = threading.Thread(target = self.parking_algo)
        t3.start()
        


    def front_cam(self):

        # Start camera
        cap = cv2.VideoCapture(2)
        # Check if the webcam is opened correctly
        if not cap.isOpened():
            raise IOError("Cannot open webcam")
        
        while self.cam1 is True:
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
            self.center = rec.detect_circle(blur)
            self.dir = rec.park_dir(frame, self.center)
            
        cap.release()
        cv2.destroyAllWindows()

    def parking_algo(self):
        self.state = 1
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
                prev_state = self.corr_entry()
                if prev_state == 4:
                    self.state = 2
                else:
                    print("End state 4!!!!!!!")
                    ser.write('p'.encode())
                    time.sleep(3)
                    self.state = self.state + 1
            elif self.state == 5:
                '''
                time.sleep(1.5)
                ser.write('q'.encode())
                time.sleep(0.9)
                ser.write('k'.encode())
                time.sleep(0.9)
                ser.write('j'.encode())
                '''
                self.park()
                self.state = self.state + 1
            elif self.state == 6:
                self.park_adjust()
                self.state = self.state + 1
            '''
            elif self.state == 7:
                #self.lift()
                try:
                    print("Lift up")
                    time.sleep(1.5)
                    ser.write('q'.encode())
                    time.sleep(1.5)
                    ser.write('k'.encode())
                    time.sleep(1.5)
                    ser.write('j'.encode())
                    print('Delivery complete')
                    time.sleep(1.5)
                    print('Leaving')
                    ser.write('w'.encode())
                    time.sleep(1.5)
                    ser.write('p'.encode())
                except:
                    pass
                self.state = self.state + 1
            '''
            
                
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
        ser.write('t'.encode())
        while True:
            try:
                poles = self.pole_cnts
                if len(poles) > 1:
                    break
            except:
                pass
        ser.write('p'.encode())
        time.sleep(1)
        print("end state 1")
    
    def align(self):
        print("Align with midpoint")
        while True:
            try:
                target = self.target
                print(target)
                if target > -10:
                    ser.write('t'.encode())
                    time.sleep(0.1)
                    ser.write('p'.encode())
                    time.sleep(0.1)
                elif target < -15:
                    ser.write('g'.encode())
                    time.sleep(0.1)
                    ser.write('p'.encode())
                    time.sleep(0.1)
                else:
                    break
            except:
                pass
        print("Aligned with midpoint!!!!!!!")
        ser.write('p'.encode())
        time.sleep(1)
    
    def forward(self):
        print("Going Forward")
        ser.write('w'.encode())
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
        prev_state = 0
        while True:
            try:
                side = self.side
                entry = self.entry
                
                #print(side)
                if entry is True:
                    self.align()
                    break
                    '''
                    print("Entry 0")
                    entry_confirm = True
                    for i in range(1):
                        if self.entry is False:
                            entry_confirm = False
                        
                    if entry_confirm is True:
                        break
                    '''
                elif side == "left":
                    print("slide right")
                    ser.write('d'.encode()) # move right
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

        return prev_state

    def park(self):
        self.cam1 = False
        self.t2.start()
        ser.write('d'.encode())
        time.sleep(0.7)
        ser.write('p'.encode())
        print("Forward")
        ser.write('w'.encode())
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
        print("Park adjust")
        while True:
            try:
                nav = []
                x_diff = self.dir[0]
                y_diff = self.dir[1]
                if x_diff < -80:
                    print("Go backward")
                    ser.write('s'.encode())
                    time.sleep(0.1)
                    ser.write('p'.encode())
                elif x_diff > 80:
                    print("Go forward")
                    ser.write('w'.encode())
                    time.sleep(0.1)
                    ser.write('p'.encode())
                if y_diff < -80:
                    print("Go right")
                    ser.write('d'.encode())
                    time.sleep(0.1)
                    ser.write('p'.encode())
                elif y_diff > 80:
                    print("Go left")
                    ser.write('a'.encode())
                    time.sleep(0.1)
                    ser.write('p'.encode())
                else:
                    print("Arrive at target.")
                    ser.write('p'.encode())
                    try:
                        print("Lift up")
                        time.sleep(1.5)
                        ser.write('q'.encode())
                        time.sleep(1.5)
                        ser.write('k'.encode())
                        time.sleep(1.5)
                        ser.write('j'.encode())
                        print('Delivery complete')
                        time.sleep(1.5)
                        print('Leaving')
                        ser.write('w'.encode())
                        time.sleep(4)
                        ser.write('p'.encode())
                    except:
                        pass
                    break
                
                time.sleep(0.5)
                print(x_diff, y_diff)
            except:
                pass


    def lift(self):
        '''continue'''
        


thread = myThread()