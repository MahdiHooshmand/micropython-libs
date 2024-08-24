import machine
import network
from ntptime import settime


def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("hooshmand", "1234abcd")
    while not wlan.isconnected():
        pass


def add(a, b):
    return a + b


connect_to_wifi()
settime()
rtc = machine.RTC()
GMT = rtc.datetime()
GMT_local = (0, 0, 0, 0, 3, 30, 0, 0)
rtc.datetime(tuple(map(add, GMT, GMT_local)))
