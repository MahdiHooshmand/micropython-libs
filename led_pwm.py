from serial_to_parallel import SerialToParallel
from led import Led

import machine


class LedPwm(Led):

    def __init__(self, serial_to_parallel: SerialToParallel, pin_index: int, pwm_pin: int, init_value: int = 0,
                 pwm_duty: int = 0, pwm_frequency: int = 1000):
        super().__init__(serial_to_parallel, pin_index, init_value)
        self.__pwm_pin = machine.Pin(pwm_pin, mode=machine.Pin.OUT)
        self.__pwm_pin.off()
        self.__pwm = machine.PWM(self.__pwm_pin)
        self.__pwm.freq(pwm_frequency)
        self.__pwm.duty(pwm_duty)

    def set_light_density(self, pwm_duty: int) -> None:
        self.__pwm.duty(pwm_duty)

    def set_pwm_frequency(self, pwm_frequency: int) -> None:
        self.__pwm.freq(pwm_frequency)
