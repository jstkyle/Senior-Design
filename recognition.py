import cv2
import numpy as np

# Regular HSV setting
#lower_yellow = np.array([20, 80, 80])
#upper_yellow = np.array([40, 255, 255])

def detect_yellow(frame):
    # filter for yellow
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([23, 100, 80])
    upper_yellow = np.array([40, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    return mask

def detect_blue(frame):
    # filter for blue
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([90, 80, 80])
    upper_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    return mask

def detect_circle(blur):
    mask = detect_blue(blur)
    # Find contours
    cnts, hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # Extract contours depending on OpenCV version
    #cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    # Iterate through contours and filter by the number of vertices 
    for c in cnts:
        if cv2.contourArea(c) > 5000:
            #print(cv2.contourArea(c))
            perimeter = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
            if len(approx) > 4:
                center, radius = cv2.minEnclosingCircle(c)
                #cv2.circle(frame, np.int0(center), int(radius), (0,255,0), thickness=2)
                #cv2.circle(frame, np.int0(center), 2, (0,0,255), thickness=10)
                return center

    return (0,0)

def detect_green(frame):
    # filter for green
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([31, 30, 50])
    upper_green = np.array([90, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    return mask

def detect_circle_green(blur):
    mask = detect_green(blur)
    # Find contours
    cnts, hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # Extract contours depending on OpenCV version
    #cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    # Iterate through contours and filter by the number of vertices 
    for c in cnts:
        
        if cv2.contourArea(c) > 50:
            #print(cv2.contourArea(c))
            perimeter = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.01 * perimeter, True)
            if len(approx) > 10:
                center, radius = cv2.minEnclosingCircle(c)
                #cv2.circle(frame, np.int0(center), int(radius), (0,255,0), thickness=2)
                #cv2.circle(frame, np.int0(center), 2, (0,0,255), thickness=10)
                return center, radius

    return (0,0), 0

def park_dir(frame, center):
    mid_x = int(frame.shape[1]/2)
    mid_y = int(frame.shape[0]/2)
    
    diff = tuple((int(center[0] - mid_x), int(center[1] - mid_y)))

    return diff

def detect_poles(blur, frame):
    edges = detect_yellow(blur)
    midpoints = []
    pole_cnts = []

    cnts, hier = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if len(cnts) == 0:
        return midpoints, pole_cnts

    for cnt in cnts:
        if cv2.contourArea(cnt) > 500:
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

def detect_side(cnts):
    if len(cnts) >= 2:
        rect1 = cv2.boundingRect(cnts[0])
        rect2 = cv2.boundingRect(cnts[1])
        if rect1[0] < rect2[0]:     # rect1 is left pole
            if rect1[3] > rect2[3]: # left pole longer
                return "left"
            else:                   # right pole longer
                return "right"
        else:                       # rect1 is right pole
            if rect1[3] > rect2[3]: # right pole longer
                return "right"
            else:                   # left pole longer
                return "left"   
    
    return "none"

def is_entry(cnts):
    if len(cnts) >= 2:
        rect1 = cv2.boundingRect(cnts[0])
        rect2 = cv2.boundingRect(cnts[1])

        if rect1[3] > rect2[3] * 0.97 and rect1[3] < rect2[3] * 1.03:
            return True
    
    return False




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
        return 0
    
    # Drawing the link
    cv2.line(frame, (mid_x, mid_y), (midpoint[0], mid_y), (0, 0, 255), 2)
    cv2.line(frame, (midpoint[0], mid_y-7), (midpoint[0], mid_y+7), (0, 0, 255), 2)

    # Drawing the frame mid-line
    cv2.line(frame, (mid_x, mid_y-15), (mid_x, mid_y+15), (255, 255, 255), 2)

    # Drawing midpoint
    cv2.circle(frame, midpoint, radius=1, color=(0, 255, 0), thickness=2)
    
    target = midpoint[0] - mid_x
    
    return target


def gap(midpoints, cnts):
    if len(cnts) == 2:
        rect1 = cv2.boundingRect(cnts[0])
        rect2 = cv2.boundingRect(cnts[1])
        rect1_height = rect1[3]
        rect2_height = rect2[3]
        avg_height = (rect1_height + rect2_height) / 2

        gap = abs(np.int0(midpoints[0][0] - midpoints[1][0]))
        #print(gap/max_height)
        
        if gap > 1.1*avg_height:
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
    

