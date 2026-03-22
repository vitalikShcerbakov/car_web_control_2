from dataclasses import dataclass

@dataclass
class MotorControl:
    GAS: int
    STEER: int

@dataclass
class MotionCommand:
    GAS: int = 0
    STEER: int = 0
    # target_speed: int = 0
    # target_angle: float = 0


@dataclass
class LastMotorCommand:
    G: int = 0
    R: int = 0