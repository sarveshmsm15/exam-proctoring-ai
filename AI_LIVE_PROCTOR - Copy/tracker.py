from deep_sort_realtime.deepsort_tracker import DeepSort

tracker = DeepSort(max_age=30)

def track(frame, persons):
    detections = []

    for bbox in persons:
        x1,y1,x2,y2 = bbox
        w = x2 - x1
        h = y2 - y1
        detections.append(([x1,y1,w,h],1.0,'person'))

    tracks = tracker.update_tracks(detections, frame=frame)

    students = []

    for t in tracks:
        if not t.is_confirmed():
            continue

        track_id = t.track_id
        l,t_,r,b = map(int,t.to_ltrb())

        students.append({
            "id": track_id,
            "bbox":[l,t_,r,b]
        })

    return students