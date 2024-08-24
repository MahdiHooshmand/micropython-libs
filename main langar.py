import machine
import time
from serial_to_parallel import SerialToParallel
from seven_segment import SevenSegment
from multi_seven_segment import MultiSevenSegment

outputs = SerialToParallel(serial=27, storage_register_clock=2, register_clock=4, ic_count=2)
seven_segment1 = SevenSegment(serial_to_parallel=outputs, a_pin_index=2, b_pin_index=3, c_pin_index=13,
                              d_pin_index=14, e_pin_index=15, f_pin_index=1, g_pin_index=0, dot_pin_index=12)
seven_segment10 = SevenSegment(serial_to_parallel=outputs, a_pin_index=6, b_pin_index=7, c_pin_index=9,
                               d_pin_index=10, e_pin_index=11, f_pin_index=5, g_pin_index=4, dot_pin_index=8)
digits = MultiSevenSegment([seven_segment10, seven_segment1])

rtc = machine.RTC()
timer = machine.Timer(1)

t = 60

D = 0
H = 1
M = 30

motor1 = machine.Pin(id=26, mode=machine.Pin.OUT)
motor1.off()
motor2 = machine.Pin(id=25, mode=machine.Pin.OUT)
motor2.off()


def release_weight():
    motor1.on()
    time.sleep(1)
    motor1.off()


def release_cylinder():
    motor2.on()
    time.sleep(1)
    motor2.off()


def timer_callback2(ti=0):
    date = rtc.datetime()
    if date[2] >= D and date[4] >= H and date[5] >= M:
        global timer
        timer.deinit()
        release_cylinder()


def timer_callback1(ti=0):
    global t
    t = t - 1
    if t >= 0:
        digits.set_value(t)
    else:
        global timer
        timer.deinit()
        timer = machine.Timer(1)
        timer.init(mode=machine.Timer.PERIODIC, period=10000, callback=timer_callback2)
        digits.off()
        release_weight()
        rtc.datetime((2000, 0, 0, 0, 0, 0, 0, 0))


timer.init(mode=machine.Timer.PERIODIC, period=1000, callback=timer_callback1)
digits.set_value(t)
