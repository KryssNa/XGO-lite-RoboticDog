import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import glob
import os
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import requests
import smtplib
import ssl

import spidev as SPI
import xgoscreen.LCD_2inch as LCD_2inch
from PIL import Image,ImageDraw,ImageFont
from key import Button
import numpy as np
from xgolib import XGO
import threading



exit_mark=False
acting=False
x=y=r=0
dog = XGO(port='/dev/ttyAMA0',version="xgolite")
fm=dog.read_firmware()
if fm[0]=='M':
    print('XGO-MINI')
    
    dog = XGO(port='/dev/ttyAMA0',version="xgomini")
    dog_type='M'
else:
    print('XGO-LITE')
    dog_type='L'
display = LCD_2inch.LCD_2inch()
display.clear()
splash = Image.new("RGB", (display.height, display.width ),"black")
display.ShowImage(splash)
button=Button()
width, height = 320, 240
camera = cv2.VideoCapture(0)
camera.set(3,width) 
camera.set(4,height) 


# Initialize 'currentname' to trigger only when a new person is identified.
currentname = "unknown"
# Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"
# Use this xml file
cascade = "haarcascade_frontalface_default.xml"
context = ssl.create_default_context()

# Function for getting the latest file
def get_latest_file(directory):
    # List all files in the directory
    files = glob.glob(os.path.join(directory, '*'))
    # Sort files by modification time
    files.sort(key=os.path.getmtime, reverse=True)
    # Return the path of the latest file
    return files[0] if files else None

# Function for setting up emails
message = "{yourName} is at your door."
from_address = "Krishna.kryss@gmail.com"
To = "Krishna.kryss@gmail.com"
password = "iqoh ikwq hmnd tpqw"
directory = "visitor"

# Function to send an email
def send_message(name, directory):
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = To
    msg['Subject'] = "You have a visitor"

    # Add message body
    msg.attach(MIMEText(message.format(yourName=name), 'plain'))

    # Get the latest file in the directory
    attachment_path = get_latest_file(directory)

    if attachment_path:
        # Open the attachment file
        with open(attachment_path, "rb") as attachment:
            # Add attachment to the message
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(attachment_path)}",
        )
        # Add attachment to message
        msg.attach(part)

    # Create a secure connection with the server and send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_address, password)
        server.sendmail(from_address, To, msg.as_string())

# cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())
detector = cv2.CascadeClassifier(cascade)

# Initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
# vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# Start the FPS counter
fps = FPS().start()

# Loop over frames from the video file stream
while True:
    # Grab the frame from the threaded video stream and resize it
    # to 500px (to speed up processing)
    # frame = vs.read()
    # frame = imutils.resize(frame, width=500)
    ret, frame = camera.read()
    if not ret:
        break # Return if no frame is captured

    # Convert the input frame from (1) BGR to grayscale (for face
    # detection) and (2) from BGR to RGB (for face recognition)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces in the grayscale frame
    rects = detector.detectMultiScale(gray, scaleFactor=1.1,
                                       minNeighbors=5, minSize=(30, 30),
                                       flags=cv2.CASCADE_SCALE_IMAGE)

    # OpenCV returns bounding box coordinates in (x, y, w, h) order
    # but we need them in (top, right, bottom, left) order, so we
    # need to do a bit of reordering
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    # Compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []

    # Loop over the facial embeddings
    for encoding in encodings:
        # Attempt to match each face in the input image to our known
        # encodings
        matches = face_recognition.compare_faces(data["encodings"],
                                                 encoding)
        name = "Unknown"

        # Check to see if we have found a match
        if True in matches:
            # Find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # Loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            # Determine the recognized face with the largest number
            # of votes (note: in the event of an unlikely tie Python
            # will select first entry in the dictionary)
            name = max(counts, key=counts.get)

            # If someone in your dataset is identified, print their name on the screen
            if currentname != name:
                currentname = name
                print(currentname)
                # Take a picture to send in the email
                img_name = "visitor/" + name + time.strftime("_%Y%m%d_%H%M%S") + ".jpg"
                cv2.imwrite(img_name, frame)
                print('Taking a picture.')

                # Now send me an email to let me know who is at the door
                send_message(name, directory)
                print('Message send successfully: ' + '\n' + 'visitor name:' + name)  # 200 status code means email sent successfully
        else:
            # If no faces are recognized, print "unknown" on the screen
            name = "Unknown"
            # Take a picture to send in the email
            img_name = "visitor/" + name + time.strftime("_%Y%m%d_%H%M%S") + ".jpg"
            cv2.imwrite(img_name, frame)
            print('Taking a picture.')

            # Now send me an email to let me know who is at the door
            send_message(name, directory)
            print('Message send successfully: ' + '\n' + 'visitor name: Unknown')

        # Update the list of names
        names.append(name)

    # Loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # Draw the predicted face name on the image - color is in BGR
        cv2.rectangle(frame, (left, top), (right, bottom),
                      (0, 255, 225), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                    .8, (0, 255, 255), 2)

    # Display the image to our screen
    # cv2.imshow("Facial Recognition is Running", frame)
    b, g, r1 = cv2.split(frame)
    image = cv2.merge((r1, g, b))
    image = cv2.flip(image, 1)
    imgok = Image.fromarray(image)
    display.ShowImage(imgok)
    if x != 0 and y != 0 and r != 0:
        print(x, y, r)
    key = cv2.waitKey(1) & 0xFF

    # If the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

    # Update the FPS counter
    fps.update()

# Stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# Do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
