from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from serial_worker import ArduinoSerial
from picamera2 import Picamera2
import cv2
from fastapi.responses import StreamingResponse
import time

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(
    main={"size": (320, 240), "format": "RGB888"}
))
picam2.start()

def gen_frames():
    while True:
        frame = picam2.capture_array()

        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(0.07)  # ~14 FPS для Pi3




app = FastAPI()

arduino = ArduinoSerial(port="/dev/ttyUSB0")

app.mount("/static", StaticFiles(directory="static"), name="static")



@app.get("/video")
def video_feed():
    return StreamingResponse(gen_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/")
def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("WS connected")

    try:
        while True:
            data = await ws.receive_json()
            gas = data.get("gas", 0)
            steer = data.get("steer", 0)
            arduino.send(gas, steer)

            info_battery = arduino.voltage_read()
            await ws.send_json(info_battery)

    except Exception as e:
        print("WS disconnected:", e)
