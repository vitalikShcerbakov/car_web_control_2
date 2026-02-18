import time

import cv2
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from picamera2 import Picamera2

from serial_worker import ArduinoSerial
from info_raspberry import read_temp, read_system_info, get_throttled_status


picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(
    main={"size": (320, 240), "format": "RGB888"}
))
picam2.start()


def gen_frames():
    while True:
        frame = picam2.capture_array()
        ret, buffer = cv2.imencode(
            '.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.07)  # ~14 FPS для Pi3


app = FastAPI()
arduino = ArduinoSerial(port="/dev/ttyUSB0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/video")
def video_feed():
    return StreamingResponse(
        gen_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame")


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    data_to_send = dict()
    await ws.accept()
    print("WS connected")
    try:
        while True:
            data = await ws.receive_json()
            gas = data.get("gas", 0)
            steer = data.get("steer", 0)
            arduino.send(gas, steer)

            info_battery = arduino.voltage_read()
            data_to_send["battery"] = info_battery
            data_to_send["raspi_temp"] = read_temp()
            data_to_send["system_info"] = read_system_info()
            data_to_send["throttled_status"] = get_throttled_status()
            await ws.send_json(data_to_send)

    except Exception as e:
        print("WS disconnected:", e)
