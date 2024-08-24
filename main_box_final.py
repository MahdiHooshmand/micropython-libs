from stepper_motor import RS485StepperMotor
from machine import UART, Pin

uart1 = UART(1, baudrate=9600, tx=33, rx=32)
p = Pin(25, Pin.OUT)
h_motor = RS485StepperMotor(uart1, p, "h_motor")
v_motor = RS485StepperMotor(uart1, p, "v_motor")
