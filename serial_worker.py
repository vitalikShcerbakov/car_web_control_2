import json
import time
import subprocess
import glob
import os

import serial
from serial.tools import list_ports
from serial.serialutil import SerialException


class ArduinoSerial:
    def __init__(self, baudrate=115200):
        try:
            port = self._find_arduino_port()
            self.ser = serial.Serial(port, baudrate, timeout=0.1)
        except SerialException as e:
            print('Error serial: ', e)

    def _find_arduino_port(self):
        """ Поиск порта arduino.
            2341, 2A03 — оригинальные Arduino
            1A86 — CH340 (клоны)
            0403 — FTDI
        """
        ARDUINO_VIDS = (0x2341, 0x2A03, 0x1A86, 0x0403)
        for port in list_ports.comports():
            if port.vid in ARDUINO_VIDS:
                return port.device
        return None

    def send(self, gas: int, steer: int):
        print(f'send: {gas} , {steer}')
        gas = max(-255, min(255, gas))
        steer = max(-255, min(255, steer))
        cmd = f"G:{gas};R:{steer}\n"
        self.ser.write(cmd.encode())

    def close(self):
        self.ser.close()

    def voltage_read(self):
        line = self.ser.readline().decode().strip()
        try:
            data = json.loads(line)
            return data
        except json.JSONDecodeError:
            # это была не телеметрия (например ответ на команду)
            print("RAW:", line)
