from machine import UART
from stepper_motor import RS485StepperMotor

uart = UART(1, baudrate=9600, tx=33, rx=32)
rs485 = RS485StepperMotor(uart, 2)
