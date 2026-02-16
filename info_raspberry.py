import psutil
import subprocess


def read_temp():
    result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
    temp_str = result.stdout.decode().strip()
    # пример: "temp=54.2'C"
    temp_val = float(temp_str.split('=')[1].replace("'C",""))
    return temp_val


def read_system_info():
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }


if __name__ == "__main__":
    print(read_temp())
    print(read_system_info())
