from machine import UART
from stepper_motor import RS485StepperMotor

stepper_motor = None
uart = UART(1, baudrate=9600, tx=33, rx=32)
rs485 = RS485StepperMotor(uart, 2)

while True:
    rs485.read()
