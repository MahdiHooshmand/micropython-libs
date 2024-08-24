import machine
import time


class ParallelToSerial:

    def __init__(self, shift: int, serial: int, clock: int, ic_count: int = 1, interrupt_pin: int = None,
                 interrupt_trigger: int = machine.Pin.IRQ_RISING,
                 interrupt_handler: Callable[[machine.Pin], Any] = None):
        self.__shift = machine.Pin(shift, mode=machine.Pin.OUT, value=1)
        self.__serial = machine.Pin(serial, mode=machine.Pin.IN)
        self.__clock = machine.Pin(clock, mode=machine.Pin.OUT, value=1)
        if interrupt_pin is not None:
            self.__interrupt = machine.Pin(interrupt_pin, mode=machine.Pin.IN)
            if interrupt_handler is not None:
                self.__interrupt.irq(trigger=interrupt_trigger, handler=interrupt_handler)
        else:
            self.__interrupt = None
        self.__ic_count = ic_count
        self.__pins = ic_count * 8
        self.__values = [0 for _ in range(ic_count * 8)]

    @property
    def values(self) -> list:
        t.sleep_ms(1)
        self.__shift.value(0)
        t.sleep_ms(1)
        self.__shift.value(1)
        t.sleep_ms(1)
        for i in range(self.__pins):
            self.__values[i] = self.__serial.value()
            t.sleep_ms(1)
            self.__clock.value(0)
            t.sleep_ms(1)
            self.__clock(1)
            t.sleep_ms(1)
        return self.__values

    def value(self, index: int) -> int:
        return self.values[index]

    @property
    def ic_count(self) -> int:
        return self.__ic_count

    @property
    def pins_count(self):
        return self.__pins
