import asyncio
from dataclasses import asdict

async def telemetry_loop(robot, manager):
    while True:
        await manager.broadcast({
            "type": "telemetry",
            "data": asdict(robot.telemetry)
        })

        await asyncio.sleep(0.05)