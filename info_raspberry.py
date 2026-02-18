import subprocess

import psutil


def read_temp():
    result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
    temp_str = result.stdout.decode().strip()
    temp_val = float(temp_str.split('=')[1].replace("'C", ""))
    return temp_val


def read_system_info():
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }


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


if __name__ == "__main__":
    print(read_temp())
    print(read_system_info())
