from serial_to_parallel import SerialToParallel
from led import Led


class ProgressLed:

    def __init__(self, serial_to_parallel: SerialToParallel, indexes: list, init_value: int = 0):
        self.__serial_to_parallel = serial_to_parallel
        self.__LEDs = []
        for led_index in indexes:
            self.__LEDs.append(Led(serial_to_parallel, led_index, 0))
        for i in range(init_value):
            self.__LEDs[i].on(commit=False)
        self.__serial_to_parallel.commit()
        self.__value = init_value

    def set_value(self, value: int, commit=True):
        for i in range(len(self.__LEDs)):
            if i < value:
                self.__LEDs[i].on(commit=False)
            else:
                self.__LEDs[i].off(commit=False)
        if commit:
            self.commit()
        self.__value = value

    def commit(self) -> None:
        self.__serial_to_parallel.commit()

    @property
    def value(self) -> int:
        return self.__value

    def increase(self, commit=True) -> None:
        if self.__value < len(self.__LEDs):
            self.set_value(self.__value + 1, commit=commit)

    def decrease(self, commit=True) -> None:
        if self.__value > 0:
            self.set_value(self.__value - 1, commit=commit)
