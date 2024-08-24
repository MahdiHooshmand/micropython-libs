from serial_to_parallel import SerialToParallel
from seven_segment import SevenSegment
from multi_seven_segment import MultiSevenSegment
from machine import Timer, Pin
import time
from ntc import NTC

serial = 27
clock = 4
storage_clock = 2
ic565 = 4
outputs = SerialToParallel(serial, storage_clock, clock, ic565)
outputs.set_values([0 for i in range(32)])
dp = 23
a = 9
b = 8
c = 22
d = 21
e = 20
f = 10
g = 11
seg1 = SevenSegment(outputs, a, b, c, d, e, f, g, dp)
dp = 19
a = 13
b = 12
c = 18
d = 17
e = 16
f = 14
g = 15
seg2 = SevenSegment(outputs, a, b, c, d, e, f, g, dp)
set_value = MultiSevenSegment([seg1, seg2])
set_value.set_value(25)
set_temp = 25.0
dp = 31
a = 1
b = 0
c = 30
d = 29
e = 28
f = 2
g = 3
seg3 = SevenSegment(outputs, a, b, c, d, e, f, g, dp)
dp = 27
a = 5
b = 4
c = 26
d = 25
e = 24
f = 6
g = 7
seg4 = SevenSegment(outputs, a, b, c, d, e, f, g, dp)
actual = MultiSevenSegment([seg3, seg4])
relay = Pin(32, Pin.OUT)
increase = Pin(25, Pin.IN)
decrease = Pin(26, Pin.IN)
temp = NTC(33)
relay_flag = 1
tim0 = Timer(0)
period = 0
actual.set_value(25)
t1, t2, t3, t4, t5, t6, t7, t8 = 0, 0, 0, 0, 0, 0, 0, 0


def callback3(t):
    temp_value = int(temp.get_t())
    global t1, t2, t3, t4, t5, t6, t7, t8
    if temp_value > 99:
        temp_value = 99
    t1, t2, t3, t4, t5, t6, t7, t8 = temp_value, t1, t2, t3, t4, t5, t6, t7
    global actual, set_value, set_temp
    actual.set_value(temp_value)
    if set_value.last > set_temp:
        set_temp = set_temp + 0.1
    elif set_value.last < set_temp:
        set_temp = set_temp - 0.1


tim1 = Timer(1)
tim1.init(period=2000, mode=Timer.PERIODIC, callback=callback3)


def callback1(t):
    relay.off()
    global period
    tim0.init(period=10000 - period, mode=Timer.ONE_SHOT, callback=callback2)


def callback2(t):
    global relay_flag
    relay_flag = 1


while True:
    if increase.value() == 1:
        if set_value.last < 99:
            set_value.set_value(set_value.last + 1)
    elif decrease.value() == 1:
        if set_value.last > 1:
            set_value.set_value(set_value.last - 1)
    if set_temp <= actual.last:
        relay.off()
    elif relay_flag == 1:
        relay.on()
        relay_flag = 0
        period = int(((set_temp - actual.last) * 700.0) - ((((t1 - t2) * 4 + (t2 - t3) * 2 + (t3 - t4) * 2 + (
                t4 - t5) * 1 + (t5 - t6) * 1 + (t6 - t7) * 1 + (t7 - t8) * 1) / 12.0) * 16000.0))
        if period > 9999:
            period = 9999
        elif period < 1:
            period = 1
        tim0.init(period=period, mode=Timer.ONE_SHOT, callback=callback1)
        time.sleep_ms(100)
        outputs.commit()
    time.sleep_ms(100)
