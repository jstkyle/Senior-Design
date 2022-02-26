import cv2
import recognition as rec
import time
import numpy as np
import opencv_plot

class Graph:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.graph = np.zeros((height, width, 3), np.uint8)
    def update_frame(self, value):
        if value < 0:
            value = 0
        elif value >= self.height:
            value = self.height - 1
        new_graph = np.zeros((self.height, self.width, 3), np.uint8)
        new_graph[:,:-1,:] = self.graph[:,1:,:]
        new_graph[self.height - value:,-1,:] = 255
        self.graph = new_graph
    def get_graph(self):
        return self.graph

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

# Surrounding mapping
graph = Graph(100,60)

while True:
    # Start time
    start = time.time()

    ret, frame = cap.read()

    if frame is None:
        print("No frame")
        break

    blur = cv2.GaussianBlur(frame,(5,5),0)
    edges = rec.detect_yellow(blur)
    contours = rec.contour(edges)
    midpoints, pole_cnts = rec.detect_poles(contours,frame)
    rec.dist(frame, pole_cnts)
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

    graph.update_frame(1)
    roi = frame[-70:-10, -110:-10,:]
    roi[:] = graph.get_graph()
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()
