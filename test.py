import cv2

# Load pre-trained face detection model
model_file = "res10_300x300_ssd_iter_140000_fp16.caffemodel"
config_file = "deploy.prototxt"
net = cv2.dnn.readNetFromCaffe(config_file, model_file)

# Read the image
image_path = 'input.jpg'  # Replace with the path to your image
img = cv2.imread(image_path)

# Resize image for better processing speed
resized_img = cv2.resize(img, (300, 300))

# Convert image to blob for input to the deep learning model
blob = cv2.dnn.blobFromImage(resized_img, 0.007843, (300, 300), 127.5)

# Set the blob as input to the model
net.setInput(blob)

# Run forward pass to get face detections
detections = net.forward()

# Loop over the detections
for i in range(detections.shape[2]):
    confidence = detections[0, 0, i, 2]
    if confidence > 0.5:  # Adjust confidence threshold as needed
        # Get the coordinates of the bounding box
        box = detections[0, 0, i, 3:7] * np.array([img.shape[1], img.shape[0], img.shape[1], img.shape[0]])
        (startX, startY, endX, endY) = box.astype("int")

        # Draw the bounding box around the face
        cv2.rectangle(img, (startX, startY), (endX, endY), (0, 255, 0), 2)

# Display the result
cv2.imshow('Detected Faces', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
