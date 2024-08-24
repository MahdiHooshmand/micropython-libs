from machine import UART, Pin
import time

uart1 = UART(1, baudrate=9600, tx=33, rx=32)
p = Pin(25, Pin.OUT)
p.off()


def send(s):
    p.on()
    time.sleep_ms(500)
    uart1.write(s)
    time.sleep_ms(500)
    p.off()


def read():
    while uart1.any() == 0:
        pass
    data = uart1.read()
    print(type(data))
    print(data)
    data = data.decode('utf8')
    print(type(data))
    print(data)




