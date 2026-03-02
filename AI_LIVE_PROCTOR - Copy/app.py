import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from flask import Flask, Response, render_template
from config import CAMERA_URL
from face_recognition_engine import load_known_faces, recognize, calculate_attention
from database import mark_attendance
from attendance import save_snapshot

app = Flask(__name__)

# Load models
person_model = YOLO("yolov8n.pt")
tracker = DeepSort(max_age=30)

load_known_faces()


def generate_frames():
    cap = cv2.VideoCapture("https://172.23.244.51:8080/mjpegfeed")
    while True:
        success, frame = cap.read()
        if not success:
            break

        # YOLO detection
        results = person_model(frame)[0]
        detections = []

        for r in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = r

            # PERSON
            if int(class_id) == 0:
                detections.append(([x1, y1, x2-x1, y2-y1], score, "person"))

            # MOBILE PHONE
            if int(class_id) == 67:
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 3)
                cv2.putText(frame, "PHONE DETECTED!",
                            (int(x1), int(y1)-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 0, 255),
                            2)

                save_snapshot(frame, "CHEATING_PHONE")

        # Tracking
        tracks = tracker.update_tracks(detections, frame=frame)

        for track in tracks:
            if not track.is_confirmed():
                continue

            l, t, w, h = track.to_ltrb()
            cv2.rectangle(frame, (int(l), int(t)),
                          (int(w), int(h)), (0, 255, 0), 2)

        # Face recognition + attention
        faces = recognize(frame)

        for x1, y1, x2, y2, name in faces:

            attention_status = calculate_attention(
                x1, y1, x2, y2, frame.shape[1]
            )

            color = (0, 255, 0)

            if attention_status == "NOT ATTENTIVE":
                color = (0, 0, 255)
                save_snapshot(frame, f"{name}_NOT_ATTENTIVE")

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            cv2.putText(frame,
                        f"{name} - {attention_status}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        color,
                        2)

            if name != "Unknown":
                mark_attendance(name)

        # Stream to browser
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               frame_bytes + b'\r\n')


@app.route('/')
def dashboard():
    return render_template("dashboard.html")


@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)