import asyncio
from dataclasses import asdict


async def telemetry_loop(robot, manager):
    while True:
        tel = robot.telemetry
        await manager.broadcast(
            {
                "telemetry": {
                    "IRSensor": asdict(tel.infrareds),
                    "ultrasonicSensor": {"distance": tel.ul1},
                },
                "encoders": asdict(tel.encoders),
                "battery": {
                    "drive": asdict(tel.battery_driver),
                    "raspberry": asdict(tel.battery_raspberry),
                },
            }
        )
        await asyncio.sleep(0.05)
