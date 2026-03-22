from fastapi import WebSocket, APIRouter

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

    @router.websocket("/ws")
    async def ws(ws: WebSocket):
        await manager.connect(ws)
        try:
            while True:
                data = await ws.receive_json()
                gas = data.get("gas", 0)
                steer = data.get("steer", 0)
                robot.manual_control = robot.gas_steer_to_motor(gas, steer)
                # robot.motion_command.target_speed = data.get("speed", 0)
        except:
            manager.disconnect(ws)

    return router