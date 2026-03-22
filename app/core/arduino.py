from serial.tools import list_ports

def find_arduino_port():
    """ Поиск порта arduino.
        2341, 2A03 — оригинальные Arduino
        1A86 — CH340 (клоны)
        0403 — FTDI
    """
    arduino_vids = (0x2341, 0x2A03, 0x1A86, 0x0403)
    for port in list_ports.comports():
        if port.vid in arduino_vids:
            print(f"find arduino port: {port.device} ")
            return port.device
    return None