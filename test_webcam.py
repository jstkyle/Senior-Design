import cv2
import recognition as rec
import time

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
    #frame = rescale_frame(frame, percent=10)

    if frame is None:
        print("No frame")
        break

    blur = cv2.GaussianBlur(frame,(5,5),0)
    edges = rec.detect_yellow(blur)
    contours = rec.contour(edges)
    midpoint = rec.steer(rec.detect_poles(contours,frame))
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

    cv2.putText(frame, "FPS: " + str(round(fps)), (0,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    cv2.putText(frame, "AVG_FPS: " + str(round(avg_fps)), (0,80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()
