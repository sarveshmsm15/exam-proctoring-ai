from ultralytics import YOLO
from config import PHONE_CONFIDENCE, PERSON_CONFIDENCE

# Stronger model for better detection
model = YOLO("yolov8s.pt")

def detect(frame):
    results = model(frame, verbose=False)[0]

    persons = []
    phones = []

    for box in results.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        # Person
        if cls == 0 and conf > PERSON_CONFIDENCE:
            persons.append([x1, y1, x2, y2])

        # Cell phone
        if cls == 67 and conf > PHONE_CONFIDENCE:
            phones.append([x1, y1, x2, y2])

    return persons, phones
