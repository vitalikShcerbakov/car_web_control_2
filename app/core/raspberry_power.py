import subprocess
import re
import time
import smbus
import os

# UPS
UPS_ADDR = 0x36
bus = smbus.SMBus(1)

def read_voltage():
    read = bus.read_word_data(UPS_ADDR, 0x02)
    swapped = ((read & 0xff) << 8) | (read >> 8)
    return swapped * 0.000078125

def read_soc():
    read = bus.read_word_data(UPS_ADDR, 0x04)
    swapped = ((read & 0xff) << 8) | (read >> 8)
    return swapped / 256

def read_power():
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
        vname = name.replace("_A","_V")
        if vname in volts:
            p = currents[name] * volts[vname]
            powers[name] = p
            total += p

    return powers, total

while True:

    os.system("clear")

    powers, total = read_power()

    print("Raspberry Pi 5 Power Monitor")
    print("=============================\n")

    print("Power Rails:")
    for k,v in powers.items():
        print(f"{k:15} {v:.3f} W")

    print("\nTOTAL POWER: %.2f W\n" % total)

    try:
        v = read_voltage()
        s = read_soc()

        print("UPS Battery:")
        print(f"Voltage : {v:.2f} V")
        print(f"Charge  : {s:.1f} %")

    except:
        print("UPS not detected")

    time.sleep(1)



