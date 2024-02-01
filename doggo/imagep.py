import cv2
import face_recognition
import tkinter as tk
from tkinter import messagebox

# Load the reference face image
reference_image = face_recognition.load_image_file("a.png")
reference_encoding = face_recognition.face_encodings(reference_image)[0]

# Create a pop-up window
root = tk.Tk()
root.withdraw()

# Open the webcam
cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Find all face locations and face encodings in the current frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    match_found = False

    for face_encoding in face_encodings:
        # Check if the detected face matches the reference face
        matches = face_recognition.compare_faces([reference_encoding], face_encoding)

        if matches[0]:
            # Set the flag to indicate a match is found
            match_found = True
    # Show pop-up message based on the match status
    if match_found:
        print("Face Recognition", "Reference Face Matched!")
    else:
        print("Face Recognition", "Reference Face Not Matched!")

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()