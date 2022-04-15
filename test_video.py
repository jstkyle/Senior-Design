import cv2
import numpy as np
import recognition as rec
import time


cap = cv2.VideoCapture('./Test_Files/Raspi_video1.mov')

fps = cap.get(cv2.CAP_PROP_FPS)
#cap.set(cv2.CAP_PROP_FPS, 60)
print("Frame per second camera: {fps}")

# Number of frames to capture
num_frames = 1

print("Capturing {numframes} frames.")

Total_time = 0
Total_frames = 0

while(cap.isOpened()):
    
    # Start time
    start = time.time()

    ret, frame = cap.read()

    if frame is None:
        print("No frame")
        break

    blur = cv2.GaussianBlur(frame, (5,5), 0)
    edges = rec.detect_yellow(blur)
    midpoints, pole_cnts = rec.detect_poles(edges, frame)
    dist = rec.dist(frame, pole_cnts)
    gap = rec.gap(midpoints, pole_cnts)
    print(gap)
    print(dist)
    midpoint = rec.steer(midpoints)
    rec.dash(frame, midpoint)

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
