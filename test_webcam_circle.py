import cv2
import recognition as rec
import time
import numpy as np


# Start camera
cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_FPS, 10)

fps = cap.get(cv2.CAP_PROP_FPS)
print("Frame per second camera: {fps}")

# Number of frames to capture
num_frames = 1

print("Capturing {numframes} frames.")

# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

Total_time = 0
Total_frames = 0


while True:
    # Start time
    start = time.time()

    ret, frame = cap.read()

    if frame is None:
        print("No frame")
        break

    mid_x = int(frame.shape[1]/2)
    mid_y = int(frame.shape[0]/2)
    
    blur = cv2.GaussianBlur(frame, (5,5), 0)
    #mask = rec.detect_green(blur)
    #center = rec.detect_circle(bDlur)
    center = rec.detect_circle(blur)
    point = (0,0)
    #dir = rec.park_dir(frame, center)
    '''
    print(dir[0])
    print(center, dir)
    if center != point:
        print(f"X diff: {dir[0]}")
        print(f"Y diff: {dir[1]}")
        '''
    #print(radius)
    cv2.circle(frame, np.int0(center), 2, (0,0,255), thickness=10)
    cv2.circle(frame, (mid_x, mid_y), 2, (255,0,0), thickness=10)
    # End time
    end = time.time()

    # Time elapsed
    seconds = end - start

    # Average fps
    Total_time += seconds
    Total_frames += 1

    # Calculate frames per second
    fps = num_frames / seconds
    avg_fps = Total_frames/Total_time

    cv2.putText(frame, "FPS: " + str(round(fps)), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    cv2.putText(frame, "AVG_FPS: " + str(round(avg_fps)), (50,80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()
