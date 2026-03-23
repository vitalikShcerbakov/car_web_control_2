from dataclasses import dataclass

@dataclass
class TelemetryData:
    timestamp: float = 0.0
    # encoder_left: int = 0
    # encoder_right: int = 0
    # ultrasonic_distance: float = 0.0
    # battery_voltage: float = 0.0
    bus_V: float = 0.0
    current_mA: float = 0.0
    power_mW: float = 0.0

    ir1: bool = True
    ir2: bool = True
    ir3: bool = True
    ir4: bool = True

    enc1: int = 0
    enc2: int = 0
    enc3: int = 0
    enc4: int = 0

    ul1: int = 0