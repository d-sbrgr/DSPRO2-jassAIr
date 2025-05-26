from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import cv2
from ultralytics import YOLO

app = FastAPI()

# Load the YOLO model from a .pt file
model = YOLO("artifacts/yolov11-finetuned-model-non-overlapping-v0/best.pt")

# Create a generator to handle the video stream
def gen_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            results = model(frame)[0]
            for result in results:
                confidence = float(result.boxes.conf)
                cls = int(result.boxes.cls)
                x1, y1, x2, y2 = result.boxes.xyxy.numpy()[0]
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, f"{model.names[int(cls)]} {confidence:.2f}", (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/")
def index():
    return Response(content="""
    <html>
        <head>
            <title>YOLO Video Stream</title>
        </head>
        <body>
            <h1>YOLO Video Stream</h1>
            <img src="/video_feed" height="480" width="640">
        </body>
    </html>
    """, media_type="text/html")