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

        t1 = threading.Thread(target = self.computer_vision)
        t1.start()
        t2 = threading.Thread(target = self.parking_algo)
        t2.start()


    def computer_vision(self):

        # Start camera
        cap = cv2.VideoCapture(0)

        # Initialize FPS
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Number of frames to capture
        num_frames = 1

        # Check if the webcam is opened correctly
        if not cap.isOpened():
            raise IOError("Cannot open webcam")

        Total_time = 0
        Total_frames = 0
        self.num = 0
        
        while True:
            self.num = self.num + 1
            #print(f"cv: {self.num}")
            
            # Start time
            start = time.time()

            ret, frame = cap.read()

            if frame is None:
                print("No frame")
                break

            blur = cv2.GaussianBlur(frame, (5,5), 0)
            edges = rec.detect_yellow(blur)
            self.midpoints, self.pole_cnts = rec.detect_poles(edges, frame)
            self.dist = rec.dist(frame, self.pole_cnts)
            self.gap = rec.gap(self.midpoints, self.pole_cnts)
            midpoint = rec.steer(self.midpoints)
            self.target = rec.dash(frame, midpoint)


            '''
            # Calculating FPS
            end = time.time()
            seconds = end - start
            Total_time += seconds
            Total_frames += 1
            fps = num_frames / seconds
            avg_fps = Total_frames/Total_time
            cv2.putText(frame, "FPS: " + str(round(fps)), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
            cv2.putText(frame, "AVG_FPS: " + str(round(avg_fps)), (50,80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
            # ---------------------
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            '''
            

        cap.release()

        cv2.destroyAllWindows()

    def parking_algo(self):
        state = 1
        while True:

            if state == 1:
                print("start spinning")
                ser.write('r'.encode())
                
                while True:
                    try:
                        poles = self.pole_cnts
                        if len(poles) == 2:
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
                        if target > 10:
                            ser.write('t'.encode())
                            ser.write('p'.encode())
                        elif target < -10:
                            ser.write('r'.encode())
                            ser.write('p'.encode())
                        else:
                            break
                    except:
                        pass
                print("Aligned with midpoint!!!!!!!")
                ser.write('p'.encode())
                time.sleep(3)
                state = state + 1
            elif state == 3:
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
                time.sleep(3)
                state = state + 1
            elif state == 4:
                print("Going Forward")
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
            elif state == 5:
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