import cv2
import numpy as np


def detect_yellow(frame):
    # filter for yellow lane lines
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([40, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    return mask

def find_min_diff(cnts):
    pass

def contour(edges):
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if len(contours) >= 2:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        print("C1: ", cv2.contourArea(contours[0]), ", C2: ", 2*cv2.contourArea(contours[1]))
        c1 = cv2.contourArea(contours[0])
        c2 = cv2.contourArea(contours[1])
        if c1 > 2*c2:
            cnts = contours[0:1]
        elif c1 < 1000 or c2 < 1000:
            cnts = ()
        else:
            cnts = contours[0:2]
    elif len(contours) == 1:
        c1 = cv2.contourArea(contours[0])
        if c1 < 1000:
            cnts = ()
        else:
            cnts = contours
    else:
        cnts = ()

    return cnts 

def detect_poles(cnts, frame):
    midpoints = []
    if len(cnts) == 0:
        return midpoints

    for cnt in cnts:
        # Find bounding rectangle
        rect = cv2.minAreaRect(cnt) #(center(x, y), (width, height), angle of rotation)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        # Filter out shapes unlike poles
        rect_width = min(rect[1])
        rect_height = max(rect[1])
        #print("Width: ", rect_width, ", 4xHeight: ", rect_height)
        if rect_height < rect_width*4:
            continue
        
        cv2.drawContours(frame, [box], 0, (255,0,0), 2)
        # Append poles midpoint
        midpoints.append(np.int0(rect[0]))
        cv2.circle(frame, np.int0(rect[0]), radius=1, color=(255, 0, 0), thickness=2)
    
    return midpoints

def steer(midpoints):
    if len(midpoints) == 2:
        midpoint = np.int0((midpoints[0] + midpoints[1])/2)
    elif len(midpoints) == 1:
        midpoint = midpoints[0]
    else:
        midpoint = []
    
    return midpoint




def dash(frame, midpoint):
    # Getting the midpoint of the frame
    mid_x = int(frame.shape[1]/2)
    mid_y = int(frame.shape[0]/2)
    #print(midpoint)

    # Reset [0,0] point to frame midpoint
    if len(midpoint) == 0:
        midpoint = [mid_x, mid_y]
    
    # Drawing the link
    cv2.line(frame, (mid_x, mid_y), (midpoint[0], mid_y), (0, 0, 255), 2)
    cv2.line(frame, (midpoint[0], mid_y-7), (midpoint[0], mid_y+7), (0, 0, 255), 2)

    # Drawing the frame mid-line
    cv2.line(frame, (mid_x, mid_y-15), (mid_x, mid_y+15), (255, 255, 255), 2)

    # Drawing midpoint
    cv2.circle(frame, midpoint, radius=1, color=(0, 255, 0), thickness=2)