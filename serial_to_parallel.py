import machine
import time


class SerialToParallel:

    def __init__(self, serial: int, storage_register_clock: int, register_clock: int,
                 ic_count: int = 1, init_values: list = None):
        self.__serial = machine.Pin(serial, mode=machine.Pin.OUT)
        self.__serial.off()
        self.__register_clock = machine.Pin(storage_register_clock, mode=machine.Pin.OUT)
        self.__register_clock.off()
        self.__storage_register_clock = machine.Pin(register_clock, mode=machine.Pin.OUT)
        self.__storage_register_clock.off()
        self.__ic_count = ic_count
        self.__pins = ic_count * 8
        if init_values is None:
            self.__values = [0 for _ in range(ic_count * 8)]
        else:
            self.__values = init_values
        self.set_values(self.__values)

    def set_values(self, values: list, commit=True) -> None:
        self.__values = values
        if commit:
            self.commit()

    def commit(self) -> None:
        for data in self.__values:
            self.__serial.value(data)
            self.__storage_register_clock.on()
            time.sleep_us(100)
            self.__storage_register_clock.off()
            time.sleep_us(100)
        self.__register_clock.on()
        time.sleep_us(100)
        self.__register_clock.off()
        time.sleep_us(100)

    def set_pin(self, index: int, value: int, commit=True) -> None:
        self.__values[index] = value
        self.set_values(self.__values, commit)

    @property
    def ic_count(self) -> int:
        return self.__ic_count

    @property
    def pins_count(self) -> int:
        return self.ic_count * 8

    def set_ic_count(self, ic_count: int) -> None:
        self.__ic_count = ic_count
        self.__pins = ic_count * 8
