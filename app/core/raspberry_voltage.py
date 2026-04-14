from smbus2 import SMBus

ADDR = 0x36

def read_voltage(bus):
    data = bus.read_word_data(ADDR, 0x02)
    swapped = ((data << 8) & 0xFF00) | (data >> 8)
    voltage = (swapped >> 4) * 1.25 / 1000
    return voltage

def read_soc(bus):
    data = bus.read_word_data(ADDR, 0x04)
    swapped = ((data << 8) & 0xFF00) | (data >> 8)
    soc = swapped / 256
    return soc

with SMBus(1) as bus:
    voltage = read_voltage(bus)
    soc = read_soc(bus)

    print(f"Voltage: {voltage:.2f} V")
    print(f"Charge: {soc:.1f} %")
