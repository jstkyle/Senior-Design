import cv2
import recognition as rec
import time
import numpy as np
import threading



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
            midpoint = rec.steer(self.midpoints)


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
                is_found = False
                while is_found is False:
                    try:
                        poles = self.pole_cnts
                        if len(poles) == 2:
                            break
                    except:
                        pass

                print("Found Target!!!!!!!")
                state = state + 1
            elif state == 2:
                print("Going Forward")
                is_reached = False
                while is_reached is False:
                    try:
                        dist = self.dist
                        print(dist)
                        if dist <= 5:
                            break
                    except:
                        pass

                print("Arrive at target.")
                state = state + 13
            elif state == 3:
                pass



thread = myThread()