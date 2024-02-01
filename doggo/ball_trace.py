import imp


import cv2
import numpy as np
import cv2


def Image_Processing():
    global x, y, r, acting
    camera = cv2.VideoCapture(0)  # Initialize the camera

    ret, frame = camera.read()
    if not ret:
        return  # Return if no frame is captured

    # Convert to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Color masks
    colors = {
        "orange": ([10, 100, 100], [20, 255, 255]),
        "red1": ([0, 100, 100], [10, 255, 255]),
        "red2": ([160, 100, 100], [180, 255, 255]),
        "green": ([45, 100, 100], [75, 255, 255]),
        "blue": ([90, 100, 100], [130, 255, 255]),
        "parrot_green": ([30, 100, 100], [45, 255, 255])
    }

    for color, (lower, upper) in colors.items():
        lower_array = np.array(lower)
        upper_array = np.array(upper)
        mask = cv2.inRange(hsv_frame, lower_array, upper_array)

        if color == "red":
            # For red, combine two ranges
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv_frame, np.array(colors["red2"][0]), np.array(colors["red2"][1])))

        # Process each color mask
        blurred_mask = cv2.medianBlur(mask, 5)
        circles = cv2.HoughCircles(blurred_mask, cv2.HOUGH_GRADIENT, 1, 20, param1=100, param2=35, minRadius=10, maxRadius=66)
        
        if not acting and circles is not None:
            for circle in circles[0]:
                x, y, r = [int(round(param)) for param in circle]
                cv2.circle(frame, (x, y), r, (0, 255, 0), 5)  # Draw the detected circle
                
Image_Processing()
                