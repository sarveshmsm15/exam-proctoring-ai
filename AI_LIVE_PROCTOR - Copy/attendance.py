import cv2
import os
from datetime import datetime

def save_snapshot(frame, roll):
    os.makedirs("snapshots", exist_ok=True)

    filename = f"snapshots/{roll}_{datetime.now().strftime('%H%M%S')}.jpg"
    cv2.imwrite(filename, frame)