import asyncio
import json
from copy import copy
from distutils import command
from time import sleep
from typing import Union

from app.models.commands import MotionCommand, Command

class ArduinoProtocol(asyncio.Protocol):
    def __init__(self, controller):
        self.controller = controller
        self.buffer = ""
        self.transport = None
        self.queue = asyncio.Queue()
        self.last_command = Command()
        self.last_driver = MotionCommand()
        self.last_state = {Command: None, MotionCommand: None}

    def connection_made(self, transport):
        self.transport = transport
        asyncio.create_task(self.writer())

    async def writer(self):
        while True:
            cmd = await self.queue.get()
            if self.transport:
                cmd = str(cmd)
                print('cmd: ', cmd)
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

    async def send_command(self, control: Union[Command, MotionCommand]):
        try:
            if self.last_state[type(control)] != control:
                print('control: ', control)
                await self.queue.put(control)
                self.last_state[type(control)] = copy(control)
        except Exception as e:
            print('error: ', e)
            pass


