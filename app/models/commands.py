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

    def __str__(self):
        return f"M1:{self.M1};M2:{self.M2};M3:{self.M3};M4:{self.M4}\n"

    def __repr__(self):
        return f"M1:{self.M1};M2:{self.M2};M3:{self.M3};M4:{self.M4}\n"


# @dataclass
# class LastMotorCommand:
#     G: int = 0
#     R: int = 0

@dataclass
class Command:
    drive_battery: int = 0
    telemetry_bat: int = 1

    def __str__(self):
        return f"driverBat:{self.drive_battery};telemetryBat:{self.telemetry_bat}\n"
    #
    # def __repr__(self):
    #     return f"driverBat:{self.drive_battery};telemetryBat:{self.telemetry_bat}\n"