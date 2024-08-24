from machine import Pin, PWM, Timer, UART
import time


def func_to_pulse(func, start, stop, x_deviation, y_deviation):
    x = start
    y = func(start)
    res = [(0, 1)]
    x = x + x_deviation
    last_dir = 1
    while x <= stop:
        if func(x) - y >= y_deviation:
            if func(x) - y >= 2 * y_deviation:
                print("warning:x_deviation is too big or y_deviation is too small. increase y_deviation or decrease " +
                      "x_deviation")
            res.append((1, 1))
            res.append((0, 1))
            last_dir = 1
            y = y + y_deviation
            x = x + x_deviation
        elif y - func(x) >= y_deviation:
            if y - func(x) >= 2 * y_deviation:
                print("warning:x_deviation is too big or y_deviation is too small. increase y_deviation or decrease " +
                      "x_deviation")
            res.append((1, 0))
            res.append((0, 0))
            last_dir = 0
            y = y - y_deviation
            x = x + x_deviation
        else:
            res.append((0, last_dir))
            res.append((0, last_dir))
            x = x + x_deviation
    return res


def pulse_to_move(stepper_motors, pulses, time_deviation, timer=0):
    i = 0

    def callback(t0):
        global i
        if i >= len(pulses[0]):
            t0.deinit()
            return
        for motor_i in range(len(stepper_motors)):
            pul, dir = pulses[motor_i][i]
            stepper_motors[motor_i].dir.value(dir)
            stepper_motors[motor_i].pul.value(pul)
        i = i + 1

    t = Timer(timer)
    t.init(period=time_deviation / 2.0, mode=Timer.PERIODIC, callback=callback)


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
        self.pul_pwm = None
        self.timer = Timer(timer)

    def enable(self):
        self.ena.off()

    def disable(self):
        self.ena.on()

    def set_reference(self, reference=0):
        self._reference = reference

    def reference(self):
        return self._reference

    def set_dir(self, dir):
        if dir > 0:
            self.dir.on()
        else:
            self.dir.off()

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
        self.pul_pwm = PWM(self.pul, freq=int(500000.0 / self._speed), duty_u16=32768)

    def stop_continues_moving(self):
        self.pul_pwm.deinit()
        del self.pul_pwm
        self.pul = Pin(self._pul_index, Pin.OUT)
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


class RS485StepperMotor:
    def __init__(self, uart: UART, active_pin, name="", sleep=100):
        self.uart = uart
        self.p = active_pin
        self.p.off()
        self.sleep = sleep
        self.name = name

    def send(self, command):
        time.sleep_ms(self.sleep)
        self.p.on()
        time.sleep_ms(self.sleep)
        self.uart.write(command)
        time.sleep_ms(self.sleep)
        self.p.off()
        data = ""
        while "END" not in data:
            while self.uart.any() == 0:
                pass
            data = self.uart.read()
            data = data.decode('utf8')
            print(data)
        time.sleep_ms(self.sleep)

    def read(self):
        while self.uart.any() == 0:
            pass
        data = self.uart.read()
        data = data.decode('utf8')
        time.sleep_ms(self.sleep)
        self.p.on()
        time.sleep_ms(self.sleep)
        self.uart.write("OK\n")
        self.uart.write("Command:" + data + "\n")
        res = None
        try:
            res = eval(data)
        except Exception as e:
            self.uart.write("ERROR:")
            self.uart.write(str(e))
        if res is not None:
            self.uart.write(str(res))
        self.uart.write("\n")
        self.uart.write("END")
        time.sleep_ms(self.sleep)
        self.p.off()

    def enable(self):
        self.send(self.name + ".enable()")

    def disable(self):
        self.send(self.name + ".disable()")

    def set_reference(self, reference=0):
        self.send(self.name + ".set_reference(reference=" + str(reference) + ")")

    def reference(self):
        return self.send(self.name + ".reference()")

    def set_dir(self, dir):
        self.send(self.name + ".set_dir(dir=" + str(dir) + ")")

    def go_to_angle_absolute(self, angle):
        self.send(self.name + ".go_to_angle_absolute(angle=" + str(angle) + ")")

    def go_to_angle_relative(self, angle):
        self.send(self.name + ".go_to_angle_relative(angle=" + str(angle) + ")")

    def set_speed_pulse_width(self, pulse_width):
        self.send(self.name + ".set_speed_pulse_width(pulse_width=" + str(pulse_width) + ")")

    def set_speed_rev_per_second(self, rev_per_second):
        self.send(self.name + ".set_speed_rev_per_second(rev_per_second=" + str(rev_per_second) + ")")

    def set_speed_steps_per_second(self, steps_per_second):
        self.send(self.name + ".set_speed_steps_per_second(steps_per_second=" + str(steps_per_second) + ")")

    def set_speed_rev_per_min(self, rev_per_min):
        self.send(self.name + ".set_speed_rev_per_min(rev_per_min=" + str(rev_per_min) + ")")

    def continues_moving(self):
        self.send(self.name + ".continues_moving()")

    def stop_continues_moving(self):
        self.send(self.name + ".stop_continues_moving()")

    def swing(self, ms):
        self.send(self.name + ".swing(ms=" + str(ms) + ")")

    def stop_swing(self):
        self.send(self.name + ".stop_swing()")

    def pulse_to_move(self, stepper_motors_name, pulses, time_deviation, timer=0):
        self.send("stepper_motor.pulse_to_move(stepper_motors=" + str(stepper_motors_name) + ",pulses=" +
                  str(pulses) + ",time_deviation=" + str(time_deviation) + ",timer=" + str(timer))
