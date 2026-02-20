import time

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from serial_worker import ArduinoSerial
from info_raspberry import read_temp, read_system_info, get_throttled_status, detect_raspberry_pi
from camera_service import (
    camera_available,
    PiCameraService,
    DummyCameraService,
)

# Камера
if camera_available:
    camera = PiCameraService()
else:
    camera = DummyCameraService()

app = FastAPI()
arduino = ArduinoSerial()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/video")
def video_feed():
    if not camera_available:
        # можно либо 503
        pass
    return StreamingResponse(
        camera.gen_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame")


@app.on_event("shutdown")
def shutdown_event():
    if camera_available and hasattr(camera, "picam2"):
        camera.picam2.stop()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    is_raspberry_pi = detect_raspberry_pi()
    data_to_send = dict()
    await ws.accept()
    print("WS connected")
    try:
        while True:
            data = await ws.receive_json()
            gas = data.get("gas", 0)
            steer = data.get("steer", 0)
            arduino.send(gas, steer)

            info_arduino = arduino.port_read()
            if info_arduino is not None:
                data_to_send["battery"] = info_arduino.get("battery")
                data_to_send["obstacle"] = info_arduino.get("obstacle")
                if is_raspberry_pi:
                    data_to_send["raspi_temp"] = read_temp()
                    data_to_send["system_info"] = read_system_info()
                    data_to_send["throttled_status"] = get_throttled_status()
                await ws.send_json(data_to_send)

    except Exception as e:
        print("WS disconnected:", e)
