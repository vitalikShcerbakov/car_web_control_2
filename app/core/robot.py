import asyncio
import time
from dataclasses import asdict

from app.models.telemetry import TelemetryData
from app.models.commands import MotionCommand, MotorControl, Command
from app.core.pid import PIDController
from app.core.filters import MovingAverageFilter

class RobotController:
    def __init__(self):
        self.telemetry = TelemetryData()
        self.motion_command = MotionCommand()
        self.manual_control = MotionCommand()
        self.command = Command()

        self.speed_pid = PIDController(1.2, 0.05, 0.1)
        self.angle_pid = PIDController(2.0, 0.01, 0.2)

        self.filter = MovingAverageFilter()

    def update_telemetry(self, data):
        # self.telemetry.encoder_left = data.get('enc_left', 0)
        # self.telemetry.encoder_right = data.get('enc_right', 0)
        try:
            if data is None:
                return None
            battery_drive = data.get("battery", {}).get("drive")
            sensor_data = data.get("telemetry", {})
            encoders = data.get("encoders")
            ir_sensors = sensor_data.get("IRSensor")
            ultrasonic_sensor = sensor_data.get("ultrasonicSensor")
            if ir_sensors is not None:
                self.telemetry.ir1 = ir_sensors.get("ir1")
                self.telemetry.ir2 = ir_sensors.get("ir2")
                self.telemetry.ir3 = ir_sensors.get("ir3")
                self.telemetry.ir4 = ir_sensors.get("ir4")
            if encoders is not None:
                self.telemetry.enc1 = encoders.get("enc1")
                self.telemetry.enc2 = encoders.get("enc2")
                self.telemetry.enc3 = encoders.get("enc3")
                self.telemetry.enc4 = encoders.get("enc4")
            if ultrasonic_sensor is not None:
                self.telemetry.ul1 = ultrasonic_sensor.get("distance")
            if battery_drive is not None:
                self.telemetry.bus_V = battery_drive.get("bus_V")
                self.telemetry.current_mA = battery_drive.get("current_mA")
                self.telemetry.power_mW = battery_drive.get("power_mW")
                self.telemetry.timestamp = asyncio.get_event_loop().time()
        except Exception as e:
            print('error: ', e, 'data: ', data)
            # time.sleep(2)

    def compute_motor_control(self):
        """ Вычислить управление двигателем"""
        speed = self.get_speed()

        s = self.speed_pid.compute(self.motion_command.target_speed, speed)
        a = self.angle_pid.compute(self.motion_command.target_angle, 0)

        return MotorControl(
            int(max(-255, min(255, s - a))),
            int(max(-255, min(255, s + a)))
        )

    def gas_steer_to_motor(self, gas, steer):
        m1, m2, m3, m4 = 0, 0, 0, 0
        if steer == 0:
            m1, m2, m3, m4 = [gas] * 4
        else:
            m1, m2 = [steer] * 2
            m3, m4 = [-steer] * 2
        return MotionCommand(m1, m2, m3, m4)

    def get_speed(self):
        return self.filter.update(self.telemetry.encoder_left)

    def get_command(self, command):
        print('command: ', command)
        return Command(command)

