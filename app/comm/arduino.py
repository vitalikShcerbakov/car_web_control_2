import asyncio
import json
from distutils import command

from app.models.commands import MotionCommand, Command

class ArduinoProtocol(asyncio.Protocol):
    def __init__(self, controller):
        self.controller = controller
        self.buffer = ""
        self.transport = None
        self.queue = asyncio.Queue()
        self.last_command = Command()
        self.last_driver = MotionCommand()

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
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            # print(line)
            try:
                self.controller.update_telemetry(json.loads(line))
            except:
                pass

    async def send_command(self, control):
        # ToDo сейчас отправка толкьо по двигателяем, сделать универсальную под все команды!!!
        try:
            if isinstance(control, MotionCommand):
                cmd = f"M1:{control.M1};M2:{control.M2};M3:{control.M3};M4:{control.M4}\n"
                if self.last_driver != control:
                    await self.queue.put(cmd)
                    self.last_driver = control
            elif isinstance(control, Command):
                cmd = f"driverBat:{control.drive_battery};telemetryBat:{control.telemetry_bat}\n"
                if self.last_command != control:
                    await self.queue.put(cmd)
                    self.last_command = control
        except Exception:
            pass


