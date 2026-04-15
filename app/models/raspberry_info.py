from dataclasses import dataclass, field

@dataclass
class Power:
    total: float = 0.0
    ...

@dataclass
class Flags:
    undervoltage_now: bool = False
    freq_capped_now: bool = False
    throttled_now: bool = False
    soft_temp_limit_now: bool = False
    undervoltage_past: bool = False
    freq_capped_past: bool = False
    throttled_past: bool = False
    soft_temp_limit_past: bool = False

@dataclass
class ThrottledStatus:
    raw: str = ''
    value: int = 0
    flags: Flags = field(default_factory=Flags)
    issues_now: list = field(default_factory=list)
    issues_past: list = field(default_factory=list)
    ok: bool = True

@dataclass
class RaspberryInfo:
    temperature: float = 0.0
    voltage: float = 0.0
    charge: float = 0.0

    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_percent: float = 0.0

    power: Power = field(default_factory=Power)
    throttled_status: ThrottledStatus = field(default_factory=ThrottledStatus)


