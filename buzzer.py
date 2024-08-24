from serial_to_parallel import SerialToParallel
from machine import Timer
from led import Led


class Buzzer(Led):

    def __init__(self, serial_to_parallel: SerialToParallel, pin_index: int, timer: Timer):
        super().__init__(serial_to_parallel, pin_index)
        if timer is None:
            self.__timer = Timer(0)
        else:
            self.__timer = timer

    def beep(self, duration: int) -> None:
        def callback(buzzer: Buzzer) -> None:
            buzzer.off(commit=True)

        self.timer.init(period=duration, mode=Timer.ONE_SHOT, callback=lambda t: callback(self))
        self.on(commit=True)

    def double_beep(self, on_duration: int, off_duration) -> None:
        def callback(buzzer: Buzzer) -> None:
            buzzer.off(commit=True)
            buzzer.timer.init(period=off_duration, mode=Timer.ONE_SHOT, callback=lambda t: buzzer.beep(on_duration))

        self.timer.init(period=on_duration, mode=Timer.ONE_SHOT, callback=lambda t: callback(self))
        self.on(commit=True)

    @property
    def timer(self):
        return self.__timer
