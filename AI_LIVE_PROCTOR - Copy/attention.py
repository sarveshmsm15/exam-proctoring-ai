import mediapipe as mp
import cv2
import numpy as np
from config import ATTENTION_THRESHOLD

mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(refine_landmarks=True)

def check_attention(frame, bbox):
    x1, y1, x2, y2 = bbox
    face = frame[y1:y2, x1:x2]

    if face.size == 0:
        return True

    rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return True

    landmarks = results.multi_face_landmarks[0]

    # Important landmark points
    nose = landmarks.landmark[1]
    left_eye = landmarks.landmark[33]
    right_eye = landmarks.landmark[263]
    left_iris = landmarks.landmark[468]
    right_iris = landmarks.landmark[473]

    # -----------------------------
    # HEAD TILT DETECTION
    # -----------------------------
    head_vertical = abs(nose.y - 0.5)

    if head_vertical * 180 > ATTENTION_THRESHOLD:
        return False

    # -----------------------------
    # EYE HORIZONTAL MOVEMENT
    # -----------------------------
    eye_center_x = (left_eye.x + right_eye.x) / 2
    iris_center_x = (left_iris.x + right_iris.x) / 2

    horizontal_movement = abs(iris_center_x - eye_center_x)

    if horizontal_movement > 0.05:
        return False

    # -----------------------------
    # EYE VERTICAL MOVEMENT
    # -----------------------------
    eye_center_y = (left_eye.y + right_eye.y) / 2
    iris_center_y = (left_iris.y + right_iris.y) / 2

    vertical_movement = abs(iris_center_y - eye_center_y)

    if vertical_movement > 0.05:
        return False

    return True