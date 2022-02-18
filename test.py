import os
import re
import cv2
import numpy as np
#from tqdm import tqdm_notebook

image = cv2.imread('Yellowpole2.jpeg')
img_grey = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
img_blur = cv2.GaussianBlur(img_grey, (5,5), 0)



def detect_edges(frame):
    # filter for yellow lane lines
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # detect edges
    edges = cv2.Canny(mask, 200, 400)

    return edges

edges = detect_edges(img_blur)

#img_concate_Hori = np.concatenate((image,edges),axis=1)
cv2.imshow("pic", edges)
cv2.waitKey(0)