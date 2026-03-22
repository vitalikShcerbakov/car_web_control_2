import asyncio

async def control_loop(robot, get_proto):
    while True:
        arduino_proto = get_proto()
        motor_control = robot.manual_control  # берём актуальное состояние robot
        if arduino_proto:
            await arduino_proto.send_command(motor_control)  # отправляем Arduino
        await asyncio.sleep(0.02)