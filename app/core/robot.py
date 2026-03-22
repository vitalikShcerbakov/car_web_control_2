import asyncio
from dataclasses import asdict

from app.models.telemetry import TelemetryData
from app.models.commands import MotionCommand, MotorControl
from app.core.pid import PIDController
from app.core.filters import MovingAverageFilter

class RobotController:
    def __init__(self):
        self.telemetry = TelemetryData()
        self.motion_command = MotionCommand()
        self.manual_control = MotionCommand()

        self.speed_pid = PIDController(1.2, 0.05, 0.1)
        self.angle_pid = PIDController(2.0, 0.01, 0.2)

        self.filter = MovingAverageFilter()

    def update_telemetry(self, data):
        self.telemetry.encoder_left = data.get('enc_left', 0)
        self.telemetry.encoder_right = data.get('enc_right', 0)
        self.telemetry.timestamp = asyncio.get_event_loop().time()

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
        # left = max(-255, min(255, gas + steer))
        # right = max(-255, min(255, gas - steer))
        return MotorControl(gas, steer)

    def get_speed(self):
        return self.filter.update(self.telemetry.encoder_left)