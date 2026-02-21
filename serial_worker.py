import json
import time
import subprocess
import glob
import os

import serial
from serial.tools import list_ports
from serial.serialutil import SerialException


class ArduinoSerial:
    def __init__(self, baud_rate=115200):
        try:
            port = self._find_arduino_port()
            self.ser = serial.Serial(port, baud_rate, timeout=0.1)
        except SerialException as e:
            print('Error serial: ', e)

    def _find_arduino_port(self):
        """ Поиск порта arduino.
            2341, 2A03 — оригинальные Arduino
            1A86 — CH340 (клоны)
            0403 — FTDI
        """
        arduino_vids = (0x2341, 0x2A03, 0x1A86, 0x0403)
        for port in list_ports.comports():
            if port.vid in arduino_vids:
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

    def port_read(self):
        line = self.ser.readline().decode().strip()
        try:
            data = json.loads(line)
            return data
        except json.JSONDecodeError:
            # это была не телеметрия (например ответ на команду)
            print("RAW:", line)

    def reset(self):
        """ Перезагрзка arduino"""
        self.ser.setDTR(False)
        time.sleep(0.1)
        self.ser.setDTR(True)
        print("arduino перезагруженна.")
