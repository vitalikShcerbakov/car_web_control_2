import asyncio
import json
from app.models.commands import LastMotorCommand

class ArduinoProtocol(asyncio.Protocol):
    def __init__(self, controller):
        self.controller = controller
        self.buffer = ""
        self.transport = None
        self.queue = asyncio.Queue()
        self.last_command = LastMotorCommand()

    def connection_made(self, transport):
        self.transport = transport
        asyncio.create_task(self.writer())

    async def writer(self):
        while True:
            cmd = await self.queue.get()
            if self.transport:
                self.transport.write(cmd.encode())

    def data_received(self, data):
        self.buffer += data.decode()
        print("data_received: ", self.buffer)
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            try:
                self.controller.update_telemetry(json.loads(line))
            except:
                pass

    async def send_command(self, control):
        cmd = f"G:{control.GAS};R:{control.STEER}\n"
        if self.last_command.R != control.STEER or self.last_command.G != control.GAS:
            await self.queue.put(cmd)
            self.last_command.G = control.GAS
            self.last_command.R = control.STEER