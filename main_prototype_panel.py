from serial_to_parallel import SerialToParallel
from progress_led_pwm import ProgressLedPwm
from seven_segment import SevenSegment
from multi_seven_segment import MultiSevenSegment
from machine import Timer
from parallel_to_serial import ParallelToSerial
from button import Button

ic595 = 8
ic165 = 3

stp = SerialToParallel(serial=5, storage_register_clock=16, register_clock=15, ic_count=8,
                       init_values=[0 for _ in range(ic595 * 8)])
red_progress = ProgressLedPwm(serial_to_parallel=stp, indexes=[30, 31, 0, 1, 2, 3, 4, 5, 6, 7], pwm_pin=14,
                              init_light_density=5*102)
red_progress.set_value(5)
green_progress = ProgressLedPwm(serial_to_parallel=stp, indexes=[24, 25, 26, 27, 28, 29, 8, 9, 10, 11], pwm_pin=12,
                                init_light_density=5*102)
green_progress.set_value(5)
blue_progress = ProgressLedPwm(serial_to_parallel=stp, indexes=[22, 21, 20, 19, 18, 17, 15, 14, 13, 12], pwm_pin=13,
                               init_light_density=5*102)
blue_progress.set_value(5)

digit1 = SevenSegment(serial_to_parallel=stp, a_pin_index=32, b_pin_index=33, c_pin_index=38, d_pin_index=37,
                      e_pin_index=36, f_pin_index=34, g_pin_index=35, dot_pin_index=39)
digit2 = SevenSegment(serial_to_parallel=stp, a_pin_index=40, b_pin_index=41, c_pin_index=46, d_pin_index=45,
                      e_pin_index=44, f_pin_index=42, g_pin_index=43, dot_pin_index=47)
digit3 = SevenSegment(serial_to_parallel=stp, a_pin_index=48, b_pin_index=49, c_pin_index=54, d_pin_index=53,
                      e_pin_index=52, f_pin_index=50, g_pin_index=51, dot_pin_index=55)
digit4 = SevenSegment(serial_to_parallel=stp, a_pin_index=56, b_pin_index=57, c_pin_index=62, d_pin_index=61,
                      e_pin_index=60, f_pin_index=58, g_pin_index=59, dot_pin_index=63)
digits = MultiSevenSegment([digit1, digit2, digit3, digit4])
pts = ParallelToSerial(shift=2, serial=4, clock=0, ic_count=ic165)

last_key = None

timer = Timer(-1)

btn = 18

btn1 = Button(parallel_to_serial=pts, pin_index=4)
btn2 = Button(parallel_to_serial=pts, pin_index=3)
btn3 = Button(parallel_to_serial=pts, pin_index=12)
btn4 = Button(parallel_to_serial=pts, pin_index=5)
btn5 = Button(parallel_to_serial=pts, pin_index=2)
btn6 = Button(parallel_to_serial=pts, pin_index=13)
btn7 = Button(parallel_to_serial=pts, pin_index=6)
btn8 = Button(parallel_to_serial=pts, pin_index=1)
btn9 = Button(parallel_to_serial=pts, pin_index=14)
btn0 = Button(parallel_to_serial=pts, pin_index=0)
btn_clean = Button(parallel_to_serial=pts, pin_index=7)
btn_dot = Button(parallel_to_serial=pts, pin_index=15)
btn_rp = Button(parallel_to_serial=pts, pin_index=17)
btn_rm = Button(parallel_to_serial=pts, pin_index=11)
btn_gp = Button(parallel_to_serial=pts, pin_index=18)
btn_gm = Button(parallel_to_serial=pts, pin_index=10)
btn_bp = Button(parallel_to_serial=pts, pin_index=19)
btn_bm = Button(parallel_to_serial=pts, pin_index=9)


def on_key_touched(t):
    global last_key
    values = pts.values
    for i in range(ic165*8):
        if values[i] == 1:
            if i == btn1.pin:
                digits.set_value((digits.value * 10) + 1)
            elif i == btn2.pin:
                digits.set_value((digits.value * 10) + 2)
            elif i == btn3.pin:
                digits.set_value((digits.value * 10) + 3)
            elif i == btn4.pin:
                digits.set_value((digits.value * 10) + 4)
            elif i == btn5.pin:
                digits.set_value((digits.value * 10) + 5)
            elif i == btn6.pin:
                digits.set_value((digits.value * 10) + 6)
            elif i == btn7.pin:
                digits.set_value((digits.value * 10) + 7)
            elif i == btn8.pin:
                digits.set_value((digits.value * 10) + 8)
            elif i == btn9.pin:
                digits.set_value((digits.value * 10) + 9)
            elif i == btn0.pin:
                digits.set_value((digits.value * 10) + 0)
            elif i == btn_clean.pin:
                digits.off()
            elif i == btn_rm.pin:
                red_progress.decrease()
                red_progress.set_light_density(red_progress.value*102)
            elif i == btn_rp.pin:
                red_progress.increase()
                red_progress.set_light_density(red_progress.value * 102)
            elif i == btn_gm.pin:
                green_progress.decrease()
                green_progress.set_light_density(green_progress.value * 102)
            elif i == btn_gp.pin:
                green_progress.increase()
                green_progress.set_light_density(green_progress.value * 102)
            elif i == btn_bm.pin:
                blue_progress.decrease()
                blue_progress.set_light_density(blue_progress.value * 102)
            elif i == btn_bp.pin:
                blue_progress.increase()
                blue_progress.set_light_density(blue_progress.value * 102)


timer.init(period=100, mode=Timer.PERIODIC, callback=on_key_touched)
