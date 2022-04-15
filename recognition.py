import cv2
import numpy as np


def detect_yellow(frame):
    # filter for yellow
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([25, 100, 80])
    upper_yellow = np.array([40, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    return mask


def detect_poles(edges, frame):
    midpoints = []
    pole_cnts = []

    cnts, hier = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if len(cnts) == 0:
        return midpoints, pole_cnts

    for cnt in cnts:
        if cv2.contourArea(cnt) > 100:
            # Find bounding rectangle
            rect = cv2.minAreaRect(cnt) #(center(x, y), (width, height), angle of rotation)
            box = cv2.boxPoints(rect)
            box = np.int0(box)

            # Filter out shapes unlike poles
            rect_width = min(rect[1])
            rect_height = max(rect[1])
            #print("Width: ", rect_width, ", 4xHeight: ", rect_height)
            if rect_height < rect_width * 4:
                continue
            
            cv2.drawContours(frame, [box], 0, (255,0,0), 2)
            # Append poles midpoint
            midpoints.append(np.int0(rect[0]))
            pole_cnts.append(cnt)
            cv2.circle(frame, np.int0(rect[0]), radius=1, color=(255, 0, 0), thickness=2)
    
    return midpoints, pole_cnts

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

def gap(midpoints, cnts):
    if len(cnts) == 2:
        rect1 = cv2.minAreaRect(cnts[0])
        rect2 = cv2.minAreaRect(cnts[1])
        rect1_height = max(rect1[1])
        rect2_height = max(rect2[1])
        max_height = max(rect1_height, rect2_height)

        gap = abs(np.int0(midpoints[0][0] - midpoints[1][0]))
        
        if gap > max_height:
            return True
    
    return False

def dist(frame, cnts):

    # Configuration varies between cameras
    distance = 24  # inches
    pole_length = 12    # inches
    pixel_length = 690  # pixels
    focal_length = (pixel_length * distance) / pole_length

    D_list = []

    for cnt in cnts:
        # Find bounding rectangle
        rect = cv2.minAreaRect(cnt) #(center(x, y), (width, height), angle of rotation)
        mid_pnt = np.int0(rect[0])
        # Get pole height
        rect_height = max(rect[1])


        D = (pole_length * focal_length) / rect_height
        D_list.append(D)

        cv2.putText(frame, str(round(D)) + "\"", (mid_pnt[0]-5, mid_pnt[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,255))

    if len(D_list) == 0:
        avg_dist = 1000
    else:
        avg_dist = (sum(D_list) / len(D_list))
    
    return avg_dist
    

