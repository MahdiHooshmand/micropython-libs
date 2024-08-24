from stepper_motor import StepperMotor, RS485StepperMotor
from machine import UART, Pin

h_motor = StepperMotor(22, 18, 23, 6400, 1, 0)
v_motor = StepperMotor(21, 5, 19, 6400, 1, 1)
h_motor.enable()
v_motor.enable()

uart1 = UART(1, baudrate=9600, tx=33, rx=32)
rs485 = RS485StepperMotor(uart1, Pin(25, Pin.OUT))

while True:
    rs485.read()
