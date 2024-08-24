from serial_to_parallel import SerialToParallel

class Led:

    def __init__(self, serial_to_parallel: SerialToParallel, pin_index: int, init_value: int = 0):
        self.__serial_to_parallel = serial_to_parallel
        self.__pin_index = pin_index
        self.set_value(init_value)
        self.__value = init_value

    def on(self, commit=True) -> None:
        self.__serial_to_parallel.set_pin(index=self.__pin_index, value=1, commit=commit)
        self.__value = 1

    def off(self, commit=True) -> None:
        self.__serial_to_parallel.set_pin(index=self.__pin_index, value=0, commit=commit)
        self.__value = 0

    def set_value(self, value: int, commit=True) -> None:
        self.__serial_to_parallel.set_pin(index=self.__pin_index, value=value, commit=commit)
        self.__value = value

    def commit(self) -> None:
        self.__serial_to_parallel.commit()

    def value(self) -> int:
        return self.__value
