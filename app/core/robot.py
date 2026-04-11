import asyncio

from app.models.telemetry import TelemetryData
from app.models.commands import MotionCommand, MotorControl, Command


class RobotController:
    def __init__(self):
        self.telemetry = TelemetryData()
        self.motion_command = MotionCommand()
        self.manual_control = MotionCommand()
        self.command = Command()

    def update_telemetry(self, data):
        battery_driver = None
        battery_raspberry = None
        try:
            if data is None:
                return None
            battery = data.get("battery")
            if battery is not None:
                battery_driver = battery.get("drive")
                battery_raspberry = battery.get("raspberry")
                self.telemetry.telemetry_voltage = battery.get("telemetryPower_V")

            sensor_data = data.get("telemetry", {})
            encoders = data.get("encoders")
            ir_sensors = sensor_data.get("IRSensor")
            ultrasonic_sensor = sensor_data.get("ultrasonicSensor")
            if ir_sensors is not None:
                self.telemetry.infrareds.ir1 = ir_sensors.get("ir1")
                self.telemetry.infrareds.ir2 = ir_sensors.get("ir2")
                self.telemetry.infrareds.ir3 = ir_sensors.get("ir3")
                self.telemetry.infrareds.ir4 = ir_sensors.get("ir4")
            if encoders is not None:
                self.telemetry.encoders.enc1 = encoders.get("enc1")
                self.telemetry.encoders.enc2 = encoders.get("enc2")
                self.telemetry.encoders.enc3 = encoders.get("enc3")
                self.telemetry.encoders.enc4 = encoders.get("enc4")
            if ultrasonic_sensor is not None:
                self.telemetry.ul1 = ultrasonic_sensor.get("distance")
            if battery_driver is not None:
                self.telemetry.battery_driver.bus_V = battery_driver.get("bus_V")
                self.telemetry.battery_driver.current_mA = battery_driver.get("current_mA")
                self.telemetry.battery_driver.power_mW = battery_driver.get("power_mW")
                self.telemetry.battery_driver.timestamp = asyncio.get_event_loop().time()
            if battery_raspberry is not None:
                self.telemetry.battery_raspberry.bus_V = battery_raspberry.get("bus_V")
                self.telemetry.battery_raspberry.current_mA = battery_raspberry.get("current_mA")
                self.telemetry.battery_raspberry.power_mW = battery_raspberry.get("power_mW")
                self.telemetry.battery_raspberry.timestamp = asyncio.get_event_loop().time()

        except Exception as e:
            print('error: ', e, 'data: ', data)

    def gas_steer_to_motor(self, gas, steer):
        if steer == 0:
            m1, m2, m3, m4 = [gas] * 4
        else:
            m1, m2 = [steer] * 2
            m3, m4 = [-steer] * 2
        return MotionCommand(m1, m2, m3, m4)
