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
        cap = cv2.VideoCapture(0)
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
            self.green_center, self.radius = rec.detect_circle_green(blur)
            self.green_dir = rec.park_dir(frame, self.green_center)
            
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
        self.state = 1
        prev_state = 0
        while True:

            if self.state == 1:
                self.search()
                self.state = self.state + 1
            elif self.state == 2:
                self.align()
                self.state = self.state + 1
            elif self.state == 3:
                self.forward()
                self.state = self.state + 1
            elif self.state == 4:
                self.corr_entry()
                self.align()
                print("End state 4!!!!!!!")
                time.sleep(0.5)
                ser.write('p'.encode())
                time.sleep(0.5)
                self.state = self.state + 1
            elif self.state == 5:
                self.forward_2()
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
                #print(len(poles))
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
                #print(target)
                if target > -10:
                    # right rotate
                    ser.write('t'.encode())
                    time.sleep(0.1)
                    ser.write('p'.encode())
                    time.sleep(0.1)
                elif target < -15:
                    # left rotate
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
        while True:
            try:
                side = self.side
                entry = self.entry
                
                if entry is True:
                    break
                else:
                    ser.write('l'.encode())
                    time.sleep(0.3)
            except:
                pass


    def forward_2(self):
        print("Forward_2")
        ser.write('w'.encode())
        while True:
            try:
                green_center = self.green_center
                x_diff = self.green_dir[0]
                radius = self.radius
                print(radius)
                #print(f"x_diff: {x_diff}, center: {green_center}")
                if radius > 17:
                    #print(self.radius)
                    break
                elif (x_diff < -20 or x_diff > 20) and green_center != (0,0):
                    ser.write('p'.encode())
                    time.sleep(0.5)
                    while True:
                        print("Adjust")
                        try:
                            x_diff = self.green_dir[0]
                            if x_diff > 30:
                                # right rotate
                                print("right rotate")
                                ser.write('t'.encode())
                                time.sleep(0.1)
                                ser.write('p'.encode())
                                time.sleep(0.2)
                            elif x_diff < -10:
                                # left rotate
                                print("left rotate")
                                ser.write('g'.encode())
                                time.sleep(0.1)
                                ser.write('p'.encode())
                                time.sleep(0.2)
                            else:
                                break
                        except:
                            pass
                        ser.write('w'.encode())
                        time.sleep(2)
                    ser.write('w'.encode())
            except:
                pass
        
        print("Arrived_2")
        ser.write('p'.encode())
        time.sleep(2)

    def park(self):
        self.cam1 = False
        self.t2.start()
        time.sleep(2)
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
        time.sleep(0.3)
    
    def park_adjust(self):
        print("Park adjust")
        while True:
            try:
                nav = []
                x_diff = self.dir[0]
                y_diff = self.dir[1]
                print(f"x: {x_diff}, y: {y_diff}")
                if x_diff < -40:
                    print("Go backward")
                    ser.write('s'.encode())
                    time.sleep(0.2)
                    ser.write('p'.encode())
                elif x_diff > 40:
                    print("Go forward")
                    ser.write('w'.encode())
                    time.sleep(0.2)
                    ser.write('p'.encode())
                elif y_diff < -40:
                    print("Go right")
                    ser.write('d'.encode())
                    time.sleep(0.2)
                    ser.write('p'.encode())
                elif y_diff > 40:
                    print("Go left")
                    ser.write('a'.encode())
                    time.sleep(0.2)
                    ser.write('p'.encode())
                else:
                    print("Arrive at target.")
                    print("Lift up")
                    ser.write('q'.encode())
                    time.sleep(1.1)
                    ser.write('k'.encode())
                    time.sleep(1.1)
                    ser.write('j'.encode())
                    print('Delivery complete')
                    time.sleep(1.5)
                    print('Leaving')
                    ser.write('w'.encode())
                    time.sleep(4)
                    ser.write('p'.encode())
                    break
                
                time.sleep(0.5)
                print(x_diff, y_diff)
            except:
                pass


    def lift(self):
        '''continue'''
        


thread = myThread()