from machine import Pin, PWM, Timer
import time


class StepperMotor:
    def __init__(self, dir_pin_index, ena_pin_index, pul_pin_index, pulse_per_revolution=3200, gearbox_ratio=1,
                 timer=0):
        self.dir = Pin(dir_pin_index, Pin.OUT)
        self.dir.off()
        self.ena = Pin(ena_pin_index, Pin.OUT)
        self.ena.off()
        self.pul = Pin(pul_pin_index, Pin.OUT)
        self._pul_index = pul_pin_index
        self.pul.off()
        self.revolution_ratio = pulse_per_revolution * gearbox_ratio
        self._reference = 0
        self._speed = 25
        self.timer = Timer(timer)

    def enable(self):
        self.ena.off()

    def disable(self):
        self.ena.on()

    def set_reference(self, reference=0):
        self._reference = reference

    @property
    def reference(self):
        return self._reference

    def go_to_angle_absolute(self, angle):
        angle = float(angle)
        if self.dir.value() == 1:
            if angle >= self._reference:
                self.go_to_angle_relative(angle - self._reference)
            else:
                self.go_to_angle_relative(angle + 360 - self._reference)
        else:
            if self._reference >= angle:
                self.go_to_angle_relative(self._reference - angle)
            else:
                self.go_to_angle_relative(self._reference + 360 - angle)

    def go_to_angle_relative(self, angle):
        angle = float(angle)
        steps = (angle / 360.0) * self.revolution_ratio
        for i in range(int(steps)):
            self.pul.on()
            time.sleep_us(self._speed)
            self.pul.off()
            time.sleep_us(self._speed)
            if self.dir.value() == 1:
                self._reference = self._reference + (360.0 / self.revolution_ratio)
            else:
                self._reference = self._reference - (360.0 / self.revolution_ratio)
            while self._reference > 360:
                self._reference = self._reference - 360
            while self._reference < 0:
                self._reference = self._reference + 360

    def set_speed_pulse_width(self, pulse_width):
        pulse_width = int(pulse_width)
        self._speed = pulse_width
        if self._speed < 25:
            self._speed = 25

    def set_speed_rev_per_second(self, rev_per_second):
        rev_per_second = float(rev_per_second)
        steps_per_second = rev_per_second * self.revolution_ratio
        self.set_speed_steps_per_second(steps_per_second)

    def set_speed_steps_per_second(self, steps_per_second):
        steps_per_second = float(steps_per_second)
        self._speed = int(1000000 / (steps_per_second * 2))
        if self._speed < 25:
            self._speed = 25

    def set_speed_rev_per_min(self, rev_per_min):
        rev_per_min = float(rev_per_min)
        steps_per_second = (rev_per_min / 60.0) * self.revolution_ratio
        self.set_speed_steps_per_second(steps_per_second)

    def continues_moving(self):
        self.pul_pwm = PWM(self.pul)
        self.pul_pwm.init(freq=int(500000.0 / self._speed))

    def stop_continues_moving(self):
        self.pul_pwm.deinit()
        del self.pul_pwm
        self.pul = Pin(self._pul_index,Pin.OUT)
        self.pul.off()

    def swing(self, ms):
        def swing_timer_callback(t):
            value = self.dir.value()
            if value == 1:
                self.dir.value(0)
            else:
                self.dir.value(1)

        self.timer.init(period=ms, mode=Timer.PERIODIC, callback=swing_timer_callback)
        self.continues_moving()

    def stop_swing(self):
        self.timer.deinit()
        self.stop_continues_moving()
