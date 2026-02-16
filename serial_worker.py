import serial
import time

class ArduinoSerial:
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        time.sleep(2)

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
            bat1 = data["bat1"]
            bat2 = data["bat2"]
            ups = data["ups"]

            print(f"BAT1={bat1}V BAT2={bat2}V UPS={ups}V")

        except json.JSONDecodeError:
            # это была не телеметрия (например ответ на команду)
            print("RAW:", line)