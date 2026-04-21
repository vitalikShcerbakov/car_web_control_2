import asyncio
from dataclasses import asdict

from app.core.raspberry import Raspberry


async def telemetry_loop(robot, manager):
    raspberry = Raspberry()
    while True:
        # Update info rasbperry
        raspberry_info = robot.raspberry_info
        raspberry.update_info(raspberry_info)

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
                    "telemetry_voltage": tel.telemetry_voltage,
                },
                "raspberry_info": asdict(raspberry_info)
            }
        )
        await asyncio.sleep(0.05)
