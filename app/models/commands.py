from dataclasses import dataclass

@dataclass
class MotorControl:
    GAS: int
    STEER: int

@dataclass
class MotionCommand:
    M1: int = 0
    M2: int = 0
    M3: int = 0
    M4: int = 0
    # GAS: int = 0
    # STEER: int = 0
    # target_speed: int = 0
    # target_angle: float = 0


@dataclass
class LastMotorCommand:
    G: int = 0
    R: int = 0

@dataclass
class Command:
    drive_battery: int = 0