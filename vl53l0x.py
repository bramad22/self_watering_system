from machine import I2C
import time
import struct

class VL53L0X:
    def __init__(self, i2c, address=0x29):
        self.i2c = i2c
        self.address = address
        self._init_sensor()

    def _write_byte(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def _read_byte(self, reg):
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]

    def _read_u16(self, reg):
        data = self.i2c.readfrom_mem(self.address, reg, 2)
        return struct.unpack('<H', data)[0]

    def _init_sensor(self):
        # Minimale Initialisierung für Continuous Mode
        self._write_byte(0x88, 0x00)
        self._write_byte(0x80, 0x01)
        self._write_byte(0xFF, 0x01)
        self._write_byte(0x00, 0x00)
        self._write_byte(0x91, self._read_byte(0x91) | 0x40)
        self._write_byte(0x00, 0x01)
        self._write_byte(0xFF, 0x00)
        self._write_byte(0x80, 0x00)
        self._write_byte(0x94, 0x6B)
        time.sleep_ms(100)

    def start(self):
        self._write_byte(0x80, 0x01)
        self._write_byte(0xFF, 0x01)
        self._write_byte(0x00, 0x00)
        self._write_byte(0x91, self._read_byte(0x91) | 0x40)
        self._write_byte(0x00, 0x01)
        self._write_byte(0xFF, 0x00)
        self._write_byte(0x80, 0x00)
        self._write_byte(0x94, 0x6B)
        self._write_byte(0x83, self._read_byte(0x83) | 0x04)
        self._write_byte(0x83, 0x00)

    def read(self):
        self._write_byte(0x00, 0x01)  # Start single-shot measurement
        time.sleep_ms(50)
        return self._read_u16(0x1E)  # Read distance in mm