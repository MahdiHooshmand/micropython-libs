from serial_to_parallel import SerialToParallel

outputs = SerialToParallel(serial=27, storage_register_clock=2, register_clock=4, ic_count=5)

import ds1307
import os
import sdcard
import time

from machine import UART, Pin, I2C, SPI, Timer
from seven_segment import SevenSegment
from multi_seven_segment import MultiSevenSegment
from led import Led
from buzzer import Buzzer
import socket
import network

free_pins = [0, 1, 2, 3, 4]

# seven segments initialization
seven_segment1 = SevenSegment(serial_to_parallel=outputs, a_pin_index=10, b_pin_index=11, c_pin_index=37,
                              d_pin_index=38, e_pin_index=39, f_pin_index=9, g_pin_index=8, dot_pin_index=36)
seven_segment10 = SevenSegment(serial_to_parallel=outputs, a_pin_index=14, b_pin_index=15, c_pin_index=33,
                               d_pin_index=34, e_pin_index=35, f_pin_index=13, g_pin_index=12, dot_pin_index=32)
seven_segment100 = SevenSegment(serial_to_parallel=outputs, a_pin_index=18, b_pin_index=19, c_pin_index=29,
                                d_pin_index=30, e_pin_index=31, f_pin_index=17, g_pin_index=16, dot_pin_index=28)
seven_segment1000 = SevenSegment(serial_to_parallel=outputs, a_pin_index=22, b_pin_index=23, c_pin_index=25,
                                 d_pin_index=26, e_pin_index=27, f_pin_index=21, g_pin_index=20, dot_pin_index=24)
digits = MultiSevenSegment([seven_segment1000, seven_segment100, seven_segment10, seven_segment1])

# SD Card initialization
sd = sdcard.SDCard(SPI(2, sck=Pin(18), mosi=Pin(23), miso=Pin(19)), Pin(5))
os.mount(sd, "/sd")
sd_state = 1

# RTC Clock initialization
i2c = I2C(1)
ds = ds1307.DS1307(i2c)
ds.halt(False)

# LEDs initialization
led_sd_card = Led(serial_to_parallel=outputs, pin_index=7)
led_send = Led(serial_to_parallel=outputs, pin_index=6)

# buzzer initialization
buzzer = Buzzer(serial_to_parallel=outputs, pin_index=5, timer=Timer(0))


class Person:

    def __init__(self, name, code, tag, state=-1):
        self.name = name
        self.code = code
        self.tag = tag
        self.state = state


# downloading persons from SD Card
persons = []
with open("/sd/persons.csv", 'r') as file_persons:
    file_persons.readline()  # first line
    for line in file_persons:
        print(line)
        line_Str = line
        line_Str = line_Str.rstrip('\n')
        line_Str = line_Str.rstrip('\r')
        data = (line_Str.split(','))
        print(data)
        persons.append(Person(data[1], int(data[2]), int(data[0]), int(data[3])))
file_persons.close()
print("persons downloaded")

if 'times.csv' in os.listdir('/sd'):
    pass
else:
    # set first row of times.csv
    with open("/sd/times.csv", 'a') as file_times:
        file_times.write("TAG,NAME,STATE,CODE,YR,MN,D,H,M,S")
        file_times.write('\n')
        print("times created")
    file_times.close()
print("time table ready")

timer = Timer(1)


def show_time(t=0):
    if type(digits.last) == str:
        return
    now = ds.datetime()
    digits.show_time(now[4], now[5])


timer.init(mode=Timer.PERIODIC, period=5000, callback=show_time)
print("init finished")

date = ds.datetime()
digits.show_time(date[4], date[5])


def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("hooshmand", "1234abcd")
    while not wlan.isconnected():
        pass
    led_sd_card.on()


def send_file_to_socket(file_dir):
    HOST = "192.168.43.104"
    PORT = 65433
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    t.sleep_ms(1000)
    try:
        s.connect(socket.getaddrinfo(HOST, PORT)[0][-1])
        led_send.on()
        with open(file_dir, 'r') as file:
            for line in file:
                print(line)
                s.sendall(line)
        file.close()
    except OSError:
        buzzer.beep(100)
        print("error2" + file_dir)
        digits.set_word("ER02")
        t.sleep_ms(1000)
    s.close()


def get_persons_file():
    HOST = "192.168.43.104"
    PORT = 65433
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(socket.getaddrinfo(HOST, PORT)[0][-1])
        led_send.on()
        os.remove('sd/persons.csv')
        with open("/sd/persons.csv", 'a') as file_persons:
            while True:
                data = s.recv(1024)
                print(data)
                if not data:
                    return
                file_persons.write(data)
        file_persons.close()
    except OSError:
        buzzer.beep(100)
        print("error3")
        digits.set_word("ER03")
        t.sleep_ms(1000)
        s.close()


def write_person_time_to_file(person):
    now = ds.datetime()
    print(now[0], "/", now[1], "/", now[2], "   ", now[4], ":", now[5], ":", now[6])  # YR MN D H M S
    person.state = person.state * -1
    if person.state == -1:
        print("OUT")
        digits.set_word("OU" + str(person.code))
        buzzer.double_beep(100, 100)
    else:
        print("IN")
        digits.set_word("IN" + str(person.code))
        buzzer.beep(100)
    with open("/sd/times.csv", 'a') as file_times:
        # TAG,NAME,STATE,YR,MN,D,H,M,S
        file_times.write(str(person.tag))
        file_times.write(",")
        file_times.write(person.name)
        file_times.write(",")
        if person.state == -1:
            file_times.write("OUT")
        else:
            file_times.write("IN")
        file_times.write(person.code)
        file_times.write(",")
        file_times.write(",")
        file_times.write(str(now[0]))
        file_times.write(",")
        file_times.write(str(now[1]))
        file_times.write(",")
        file_times.write(str(now[2]))
        file_times.write(",")
        file_times.write(str(now[4]))
        file_times.write(",")
        file_times.write(str(now[5]))
        file_times.write(",")
        file_times.write(str(now[6]))
        file_times.write('\n')
    file_times.close()


def update_persons_states():
    os.remove('sd/persons.csv')
    with open("/sd/persons.csv", 'a') as file_persons:
        file_persons.write("TAG,NAME,CODE,LAST")
        file_persons.write('\n')
        for person in persons:
            file_persons \
                .write(str(person.tag))
            file_persons.write(",")
            file_persons.write(str(person.name))
            file_persons.write(",")
            file_persons.write(str(person.code))
            file_persons.write(",")
            file_persons.write(str(person.state))
            file_persons.write('\n')
    file_persons.close()


def read_tag():
    data = uart.any()
    if (0 < data < 11) or data > 11:
        print("Log:tag read")
        digits.set_word("ER01")
        print("error ", uart.read().strip())
        buzzer.beep(1000)
        t.sleep_ms(1000)
        return
    elif data == 11:
        tag_id = int(str(uart.read().strip())[2:-1])
        print(tag_id)
        for person in persons:
            if tag_id == person.tag:
                print(person.name)
                if person.name == "Persons":
                    digits.set_word("PERS")
                    buzzer.beep(100)
                    connect_to_wifi()
                    send_file_to_socket("/sd/persons.csv")
                    buzzer.beep(300)
                    led_send.off()
                    led_sd_card.off()
                    import machine
                    machine.reset()
                elif person.name == "Send":
                    digits.set_word("SEND")
                    buzzer.beep(100)
                    connect_to_wifi()
                    send_file_to_socket("/sd/times.csv")
                    buzzer.beep(300)
                    led_send.off()
                    led_sd_card.off()
                    import machine
                    machine.reset()
                elif person.name == "Read":
                    digits.set_word("READ")
                    buzzer.beep(100)
                    connect_to_wifi()
                    get_persons_file()
                    buzzer.beep(300)
                    led_send.off()
                    led_sd_card.off()
                    import machine
                    machine.reset()
                else:
                    write_person_time_to_file(person)
                    print("times created")
                    update_persons_states()
                    print("persons updated")
                    t.sleep_ms(1000)
                break
        now = ds.datetime()
        digits.show_time(now[4], now[5])


t.sleep_ms(1000)
# RFID initialization
uart = UART(2, baudrate=9600, rx=16, tx=17)

uart.read()
while True:
    read_tag()
