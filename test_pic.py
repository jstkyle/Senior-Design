import cv2
import numpy as np
import recognition as rec

frame = cv2.imread('Yellowpole7.jpg')
blur = cv2.GaussianBlur(frame,(5,5),0)

edges = rec.detect_yellow(blur)

contours = rec.contour(edges)
rec.detect_poles(contours, frame)
rec.draw_crosshair(frame)

cv2.imshow("Frame", frame)
c = cv2.waitKey(0)
