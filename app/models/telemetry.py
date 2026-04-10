from dataclasses import dataclass


@dataclass
class Battery:
    bus_V: float = 0.0
    current_mA: float = 0.0
    power_mW: float = 0.0
    timestamp: float = 0.0


@dataclass
class Infrared:
    ir1: bool = True
    ir2: bool = True
    ir3: bool = True
    ir4: bool = True


@dataclass
class Encoder:
    enc1: int = 0
    enc2: int = 0
    enc3: int = 0
    enc4: int = 0


@dataclass
class TelemetryData:
    battery_raspberry: Battery = Battery()
    battery_driver: Battery = Battery()
    infrareds: Infrared = Infrared()
    encoders: Encoder = Encoder()
    ul1: int = 0
