from fastapi import WebSocket, APIRouter

from app.core.camera_service import (
    camera_available,
    PiCameraService,
    DummyCameraService,
)

# Камера
if camera_available:
    camera = PiCameraService()
else:
    camera = DummyCameraService()


class ConnectionManager:
    def __init__(self):
        self.active = []

    async def connect(self, ws):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except:
                dead.append(ws)

        for d in dead:
            self.disconnect(d)


def router(manager, robot):
    router = APIRouter()
    key_command = {
        'light': 'drive_battery',
        'telemetry': 'telemetry_bat',
        'safety': 'safety_enable',
    }

    @router.get("/video")
    def video_feed():
        if not camera_available:
            # можно либо 503
            pass
        return StreamingResponse(
            camera.gen_frames(),
            media_type="multipart/x-mixed-replace; boundary=frame")

    @router.on_event("shutdown")
    def shutdown_event():
        if camera_available and hasattr(camera, "picam2"):
            camera.picam2.stop()

    @router.websocket("/ws")
    async def ws(ws: WebSocket):
        await manager.connect(ws)
        try:
            while True:
                data = await ws.receive_json()
                gas = data.get("gas", 0)
                steer = data.get("steer", 0)
                robot.manual_control = robot.gas_steer_to_motor(gas, steer)
                for key, value in data.items():
                    attr = key_command.get(key)
                    if attr and attr in robot.command.__dict__:
                        robot.command.__setattr__(attr, int(value))

        except Exception as e:
            print('ws error: ', type(e), e)
            manager.disconnect(ws)

    return router
