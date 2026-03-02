import cv2
import time
import winsound
from detector import detect
from tracker import track
import suspicious
from pdf_report import generate_pdf
from config import RTSP_URL

# ===============================
# SETTINGS
# ===============================
alert_cooldown = 3  # seconds between sounds
last_alert_time = 0

# Store suspicious scores
suspicious_scores = {}

# ===============================
# CONNECT TO CAMERA
# ===============================
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("❌ Unable to open phone camera stream")
    exit()

print("✅ AI LIVE PROCTOR STARTED")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    persons, phones = detect(frame)
    students = track(frame, persons)

    cheating_detected = False

    # ===============================
    # DRAW PHONE DETECTIONS
    # ===============================
    for phone in phones:
        px1, py1, px2, py2 = phone
        cv2.rectangle(frame, (px1, py1), (px2, py2), (0, 0, 255), 3)
        cv2.putText(frame,
                    "PHONE DETECTED",
                    (px1, py1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2)
        cheating_detected = True

    # ===============================
    # PROCESS STUDENTS
    # ===============================
    for s in students:
        bbox = s["bbox"]
        student_id = s["id"]
        x1, y1, x2, y2 = bbox

        if student_id not in suspicious_scores:
            suspicious_scores[student_id] = 0

        # Draw green student box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

        # Check suspicious activity
        is_suspicious = suspicious.check_suspicious(frame, student_id, bbox, phones)

        if is_suspicious:
            suspicious_scores[student_id] += 1
            cheating_detected = True

        # Display ID and Score
        cv2.putText(frame,
                    f"ID:{student_id} | Score:{suspicious_scores[student_id]}",
                    (x1, y1 - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2)

    # ===============================
    # CHEATING ALERT BANNER
    # ===============================
    if cheating_detected:

        # Big red banner
        cv2.rectangle(frame,
                      (0, 0),
                      (frame.shape[1], 80),
                      (0, 0, 255),
                      -1)

        cv2.putText(frame,
                    "⚠ CHEATING DETECTED ⚠",
                    (50, 55),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    (255, 255, 255),
                    4)

        # 🔊 Windows Beep Sound
        current_time = time.time()
        if current_time - last_alert_time > alert_cooldown:
            winsound.Beep(1000, 400)  # frequency, duration
            last_alert_time = current_time

    # ===============================
    # FOOTER PANEL
    # ===============================
    cv2.rectangle(frame,
                  (0, frame.shape[0] - 40),
                  (frame.shape[1], frame.shape[0]),
                  (40, 40, 40),
                  -1)

    cv2.putText(frame,
                "AI LIVE PROCTOR SYSTEM  |  Press Q to Generate Report",
                (20, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2)

    cv2.imshow("AI LIVE PROCTOR - PROFESSIONAL MODE", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

generate_pdf()