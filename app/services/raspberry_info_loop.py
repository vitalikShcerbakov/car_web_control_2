import asyncio

from app.core.raspberry import Raspberry

async def rasbp_info_loop(robot):
    raspberry = Raspberry()
    while True:
        raspberry_info = robot.raspberry_info
        raspberry.update_info(raspberry_info)
        if raspberry_info:
            print(raspberry_info)
        await asyncio.sleep(0.02)