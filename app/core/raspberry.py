import subprocess
import smbus
import psutil

import re

from app.models.raspberry_info import RaspberryInfo


class Raspberry:
    UPS_ADDR = 0x36
    bus = smbus.SMBus(1)

    @staticmethod
    def detect_raspberry_pi() -> bool:
        try:
            with open("/proc/device-tree/model") as f:
                model = f.read().lower()
                return "raspberry pi" in model
        except Exception:
            return False

    @staticmethod
    def read_temp():
        result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
        temp_str = result.stdout.decode().strip()
        temp_val = float(temp_str.split('=')[1].replace("'C", ""))
        return temp_val

    @staticmethod
    def read_system_info():
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }

    @staticmethod
    def get_throttled_status():
        """ Диагностика проблем с питанием и перегревом. """

        THROTTLE_FLAGS = {
            0: ("undervoltage_now", "Пониженное напряжение сейчас"),
            1: ("freq_capped_now", "Частота CPU ограничена сейчас"),
            2: ("throttled_now", "Сейчас включён троттлинг"),
            3: ("soft_temp_limit_now", "Достигнут мягкий температурный лимит сейчас"),
            16: ("undervoltage_past", "Ранее было пониженное напряжение"),
            17: ("freq_capped_past", "Ранее частота CPU ограничивалась"),
            18: ("throttled_past", "Ранее был троттлинг"),
            19: ("soft_temp_limit_past", "Ранее достигался мягкий температурный лимит"),
        }
        try:
            output = subprocess.check_output(
                ["vcgencmd", "get_throttled"],
                text=True
            ).strip()

            # throttled=0x50005 → 0x50005
            hex_value = output.split("=")[1]
            value = int(hex_value, 16)

            result = {
                "raw": hex_value,
                "value": value,
                "flags": {},
                "issues_now": [],
                "issues_past": [],
                "ok": value == 0
            }

            for bit, (key, description) in THROTTLE_FLAGS.items():
                active = bool(value & (1 << bit))
                result["flags"][key] = active

                if active:
                    if bit < 16:
                        result["issues_now"].append(description)
                    else:
                        result["issues_past"].append(description)

            return result

        except FileNotFoundError:
            return {"error": "vcgencmd not found (not a Raspberry Pi?)"}
        except Exception as e:
            return {"error": str(e)}

    @classmethod
    def read_voltage(cls):
        """ Напряжение на акб (последовательно 4 банки)"""
        read = cls.bus.read_word_data(cls.UPS_ADDR, 0x02)
        swapped = ((read & 0xff) << 8) | (read >> 8)
        return swapped * 0.000078125


    @classmethod
    def read_soc(cls):
        """ Процент заряда. """
        read = cls.bus.read_word_data(cls.UPS_ADDR, 0x04)
        swapped = ((read & 0xff) << 8) | (read >> 8)
        return swapped / 256

    @staticmethod
    def read_power():
        """ Потребляемая мощность. """
        data = subprocess.check_output(["vcgencmd", "pmic_read_adc"]).decode()

        currents = {}
        volts = {}

        for line in data.splitlines():
            m = re.search(r'(\S+)\s+(current|volt)\(\d+\)=([\d\.]+)', line)
            if m:
                name, typ, value = m.groups()
                if typ == "current":
                    currents[name] = float(value)
                else:
                    volts[name] = float(value)
        powers = {}
        total = 0
        for name in currents:
            vname = name.replace("_A", "_V")
            if vname in volts:
                p = currents[name] * volts[vname]
                powers[name] = p
                total += p
        return powers, total

    @classmethod
    def update_info(cls, obj: RaspberryInfo):
        obj.temperature = cls.read_temp()
        obj.voltage = cls.read_voltage()
        obj.charge = cls.read_soc()

        powers, total = cls.read_power()
        obj.power.total = total
        # for name, value in powers.items():
        #     obj.power.name = value

        system_info: dict = cls.read_system_info()
        obj.cpu_percent = system_info.get('cpu_percent')
        obj.memory_percent = system_info.get('memory_percent')
        obj.disk_percent = system_info.get('disk_percent')

        throttled_status = cls.get_throttled_status()
        obj.throttled_status.raw = throttled_status.get('raw')
        obj.throttled_status.value = throttled_status.get('value')
        obj.throttled_status.flags = throttled_status.get('flags')
        obj.throttled_status.issues_now = throttled_status.get('issues_now')
        obj.throttled_status.issues_past = throttled_status.get('issues_past')
        obj.throttled_status.ok = throttled_status.get('ok')




if __name__ == '__main__':
    rasp = Raspberry()
    print(rasp.detect_raspberry_pi())
    print(rasp.read_system_info())
    print(rasp.get_throttled_status())
    print(rasp.read_temp())
    print(rasp.read_voltage())
    print(rasp.read_power())
    print(rasp.read_soc())
