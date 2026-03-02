import os
import cv2
import time
from attention import check_attention

# Folder to store screenshots
SAVE_FOLDER = "screenshots"

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Store last save time per student
last_saved_time = {}

# Cooldown between screenshots (seconds)
SAVE_COOLDOWN = 5


def check_suspicious(frame, student_id, bbox, phones):
    """
    Returns:
        True  -> if suspicious activity detected
        False -> if normal
    """

    x1, y1, x2, y2 = bbox
    suspicious_flag = False

    # ===============================
    # 1️⃣ PHONE INSIDE STUDENT BOX
    # ===============================
    for phone in phones:
        px1, py1, px2, py2 = phone

        # Check if phone overlaps student bounding box
        if px1 >= x1 and py1 >= y1 and px2 <= x2 and py2 <= y2:
            suspicious_flag = True
            cv2.putText(frame,
                        "PHONE CHEATING!",
                        (x1, y2 + 25),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2)

    # ===============================
    # 2️⃣ ATTENTION CHECK
    # ===============================
    attention_ok = check_attention(frame, bbox)

    if not attention_ok:
        suspicious_flag = True
        cv2.putText(frame,
                    "LOOKING AWAY!",
                    (x1, y2 + 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2)

    # ===============================
    # 3️⃣ SAVE SCREENSHOT
    # ===============================
    if suspicious_flag:

        current_time = time.time()

        if student_id not in last_saved_time:
            last_saved_time[student_id] = 0

        # Save only after cooldown
        if current_time - last_saved_time[student_id] > SAVE_COOLDOWN:

            filename = f"{SAVE_FOLDER}/student_{student_id}_{int(current_time)}.jpg"
            cv2.imwrite(filename, frame)

            last_saved_time[student_id] = current_time
            print(f"⚠ Screenshot saved: {filename}")

    return suspicious_flag