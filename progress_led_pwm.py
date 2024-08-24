from serial_to_parallel import SerialToParallel
from progress_led import ProgressLed

import machine


class ProgressLedPwm(ProgressLed):

    def __init__(self, serial_to_parallel: SerialToParallel, indexes: list, pwm_pin: int, init_light_density: int = 0,
                 init_frequency: int = 1000):
        super().__init__(serial_to_parallel, indexes)
        self.__pwm = machine.PWM(machine.Pin(pwm_pin, mode=machine.Pin.OUT))
        self.__pwm.freq(init_frequency)
        self.__pwm.duty(init_light_density)

    def set_frequency(self, frequency: int) -> None:
        self.__pwm.freq(frequency)

    def set_light_density(self, pwm_duty: int) -> None:
        self.__pwm.duty(pwm_duty)
