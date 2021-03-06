import cv2
import recognition as rec
import time
import numpy as np


# Start camera
cap = cv2.VideoCapture(2)
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

    blur = cv2.GaussianBlur(frame, (5,5), 0)

    midpoints, pole_cnts = rec.detect_poles(blur, frame)
    center = rec.detect_circle(blur)
    dist = rec.dist(frame, pole_cnts)
    side = rec.detect_side(pole_cnts)
    entry = rec.is_entry(pole_cnts)
    midpoint = rec.steer(midpoints)
    target = rec.dash(frame, midpoint)
    print(entry, side, target)

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
