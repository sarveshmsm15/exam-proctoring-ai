import cv2
import os
import numpy as np
from ultralytics import YOLO

face_model = YOLO("yolov8n.pt")  # using lightweight model

known_faces = {}

def load_known_faces():
    folder = "known_faces"

    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        image = cv2.imread(path)

        result = face_model(image)[0]
        if len(result.boxes) > 0:
            x1, y1, x2, y2 = map(int, result.boxes.xyxy[0])
            face = image[y1:y2, x1:x2]
            embedding = cv2.resize(face, (64, 64)).flatten()

            roll = file.split(".")[0]
            known_faces[roll] = embedding

def recognize(frame):
    detected = []

    results = face_model(frame)[0]

    for box in results.boxes.xyxy:
        x1, y1, x2, y2 = map(int, box)
        face = frame[y1:y2, x1:x2]

        if face.size == 0:
            continue

        embedding = cv2.resize(face, (64, 64)).flatten()

        best_match = "Unknown"
        min_dist = 1e9

        for roll, known_embed in known_faces.items():
            dist = np.linalg.norm(known_embed - embedding)
            if dist < min_dist and dist < 3000:
                min_dist = dist
                best_match = roll

        detected.append((x1, y1, x2, y2, best_match))
        

    return detected
def calculate_attention(x1, y1, x2, y2, frame_width):
    face_center_x = (x1 + x2) // 2
    center_screen = frame_width // 2

    deviation = abs(face_center_x - center_screen)

    if deviation < frame_width * 0.1:
        return "ATTENTIVE"
    elif deviation < frame_width * 0.25:
        return "SLIGHT TURN"
    else:
        return "NOT ATTENTIVE"