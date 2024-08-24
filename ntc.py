import math
from machine import Pin, ADC


class NTC:

    def __init__(self, pin_index, b_value=3435.0, t0_in_c=25.0, r0=10000.0):
        self.b_value = b_value
        self.t0 = 273.15 + t0_in_c
        self.r0 = r0
        self.adc = ADC(Pin(pin_index))

    def get_v1(self):
        v_adc = (self.adc.read_u16()/65535.0)*0.95
        v1 = ((15.0*5.0)/17.0)-(v_adc*3.9)
        return v1

    def get_r(self):
        v1 = self.get_v1()
        i = (5.0-v1)/2000.0
        r = v1/i
        return r

    def get_t(self):
        r = self.get_r()
        t = 1.0 / (((math.log(r / self.r0)) / self.b_value) + (1 / self.t0))
        t = t-273.15
        return t

