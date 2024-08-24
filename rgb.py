from serial_to_parallel import SerialToParallel
from led_pwm import LedPwm


class RGB:

    def __init__(self, serial_to_parallel: SerialToParallel, red_pin_index: int, green_pin_index: int,
                 blue_pin_index: int, red_pwm_pin: int, green_pwm_pin: int, blue_pwm_pin: int, red_value: int = 0,
                 green_value: int = 0, blue_value: int = 0, pwm_frequency: int = 1000):
        self.__red = LedPwm(serial_to_parallel=serial_to_parallel, pin_index=red_pin_index, pwm_pin=red_pwm_pin,
                            init_value=1, pwm_duty=red_value, pwm_frequency=pwm_frequency)
        self.__green = LedPwm(serial_to_parallel=serial_to_parallel, pin_index=green_pin_index, pwm_pin=green_pwm_pin,
                              init_value=1, pwm_duty=green_value, pwm_frequency=pwm_frequency)
        self.__blue = LedPwm(serial_to_parallel=serial_to_parallel, pin_index=blue_pin_index, pwm_pin=blue_pwm_pin,
                             init_value=1, pwm_duty=blue_value, pwm_frequency=pwm_frequency)
        self.__serial_to_parallel = serial_to_parallel

    def set_rgb(self, r: int, g: int, b: int) -> None:
        self.__red.set_light_density(r)
        self.__green.set_light_density(g)
        self.__blue.set_light_density(b)

    def set_frequency(self, frequency: int) -> None:
        self.__red.set_pwm_frequency(frequency)
        self.__green.set_pwm_frequency(frequency)
        self.__blue.set_pwm_frequency(frequency)

    @property
    def red(self) -> LedPwm:
        return self.__red

    @property
    def blue(self) -> LedPwm:
        return self.__blue

    @property
    def green(self) -> LedPwm:
        return self.__green
