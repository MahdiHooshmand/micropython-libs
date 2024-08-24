from parallel_to_serial import ParallelToSerial


class Button:

    def __init__(self, parallel_to_serial: ParallelToSerial, pin_index: int):
        self.__parallel_to_serial = parallel_to_serial
        self.__pin_index = pin_index
