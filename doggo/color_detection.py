import cv2
import numpy as np

def detect_color_from_camera(lower_color, upper_color):
    # Start capturing video from the webcam
    cap = cv2.VideoCapture(0)

    while True:
        # Read a frame
        ret, frame = cap.read()

        if not ret:
            break

        # Convert the frame to HSV color space
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the range of color to detect
        lower_bound = np.array(lower_color)
        upper_bound = np.array(upper_color)

        # Create a mask for detecting the color in the given range
        mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)

        # Apply the mask to the original frame
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # Display the original and the result frames
        cv2.imshow('Frame', frame)
        cv2.imshow('Color Detection', result)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close the windows
    cap.release()
    cv2.destroyAllWindows()

# Example usage
# Define the lower and upper bounds for blue color in HSV
lower_blue = [110, 50, 50]
upper_blue = [130, 255, 255]

detect_color_from_camera(lower_blue, upper_blue)
