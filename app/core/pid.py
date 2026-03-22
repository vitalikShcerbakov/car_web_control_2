import asyncio

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.last_error = 0
        self.last_time = None

    def compute(self, setpoint, actual):
        now = asyncio.get_event_loop().time()

        if self.last_time is None:
            self.last_time = now
            return 0

        dt = now - self.last_time
        self.last_time = now

        error = setpoint - actual
        self.integral += error * dt

        derivative = (error - self.last_error) / dt if dt > 0 else 0
        self.last_error = error

        return self.kp * error + self.ki * self.integral + self.kd * derivative

    def reset(self):
        self.integral = 0
        self.last_error = 0
        self.last_time = None