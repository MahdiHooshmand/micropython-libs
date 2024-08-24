"""a module for controlling digital inputs and outputs

Author : Mahdi Hooshmand
Last Edit : 2022/12/30
Version : 1.3
"""
from typing import Callable, Any
from machine import Timer

import machine
import time
import math


class SerialToParallel:
    """for set infinity pins as digital output by 3 wire and ic 74HC595.

        this class use for driving ic 74HC595.
        datasheet: https://datasheetspdf.com/pdf-file/446162/ONSemiconductor/74HC595/1 .
        used for control infinity pins as digital low impedance outputs by 3 wire.
        this ic have a high impedance mode that not support in this version of code.

        Methods:
            SerialToParallel: construct an instance by giving 3 pins and number of ic 74HC595
            commit: commit the values
            set_values: set a list of 0 or 1 to pins
            set_pin: set 0 or 1 to a pin by giving pin index
            set_ic_count: change ic count and number of controllable pins

        Properties:
            ic_count: number of 74HC565 ic
            pins_count: number of controllable pins

        Examples:
            from serial_to_parallel import SerialToParallel
            serial = 5
            clock = 4
            storage_clock = 0
            ic565 = 3
            outputs = SerialToParallel(serial,clock,storage_clock,ic565)

            example1:
            outputs.set_values([1 for _ in range(ic565*8)])

            example2:
            import math
            outputs.set_values([math.fmod(i, 2) for i in range(ic565*8)])

            example3:
            import time
            outputs.set_values([1 for _ in range(ic565*8)])
            for i in range(ic565*8):
                outputs.set_pin(i,0)
                time.sleep(1)

        74HC595 pin map:
            PIN1 : Q1,
            PIN2 : Q2,
            PIN3 : Q3,
            PIN4 : Q4,
            PIN5 : Q5,
            PIN6 : Q6,
            PIN7 : Q7,
            PIN8 : GND,
            PIN9 : Q7',
            PIN10 : ~MR,
            PIN11 : SH_CP,
            PIN12 : ST_CP,
            PIN13 : ~OE,
            PIN14 : DS,
            PIN15 : Q0,
            PIN16 : Vcc.

        circuit schematic:
              ┌───595───┐
            ──┤Q0    Vcc├──TO Vcc
              │         │
            ──┤Q1     MR├──TO Vcc
              │         │
            ──┤Q2     DS├──TO SERIAL DATA PIN
              │         │
            ──┤Q3  ST-CP├──TO SHIFT REGISTER CLOCK PIN
              │         │
            ──┤Q4  SH-CP├──TO STORAGE REGISTER CLOCK PIN
              │         │
            ──┤Q5    Q7'├─────────────────────────────────┐
              │         │                                 │
            ──┤Q6     OE├──TO GND                         │
              │         │                                 │
            ──┤Q7    GND├──TO GND                         │
              └─────────┘                                 │
                                                          │
              ┌───595───┐                                 │
            ──┤Q0    Vcc├──TO Vcc                         │
              │         │                                 │
            ──┤Q1     MR├──TO Vcc                         │
              │         │                                 │
            ──┤Q2     DS├─────────────────────────────────┘
              │         │
            ──┤Q3  ST-CP├──TO SHIFT REGISTER CLOCK PIN
              │         │
            ──┤Q4  SH-CP├──TO STORAGE REGISTER CLOCK PIN
              │         │
            ──┤Q5    Q7'├─────────────────────────────────┐
              │         │                                 │
            ──┤Q6     OE├──TO GND                         │
              │         │                                 │
            ──┤Q7    GND├──TO GND                         │
              └─────────┘                                 │
                   .                                      .
                   .                                      .
                   .                                      .
              ┌───595───┐                                 │
            ──┤Q0    Vcc├──TO Vcc                         │
              │         │                                 │
            ──┤Q1     MR├──TO Vcc                         │
              │         │                                 │
            ──┤Q2     DS├─────────────────────────────────┘
              │         │
            ──┤Q3  ST-CP├──TO SHIFT REGISTER CLOCK PIN
              │         │
            ──┤Q4  SH-CP├──TO STORAGE REGISTER CLOCK PIN
              │         │
            ──┤Q5    Q7'├──NOT CONNECT
              │         │
            ──┤Q6     OE├──TO GND
              │         │
            ──┤Q7    GND├──TO GND
              └─────────┘

        """

    def __init__(self, serial: int, storage_register_clock: int, register_clock: int,
                 ic_count: int = 1, init_values: list = None):
        """construct an instance of SerialToParallel and save pins and init values

        :param serial: serial data pin id that connected to pin 14 of ic 74HC595 (DS)
        :param register_clock: shift register clock pin id that connected to pin 11 of ic 74HC595 (SHCP)
        :param storage_register_clock: storage register clock pin id that connected to pin 12 of ic 74HC595 (STCP)
        :param ic_count: the number of ic 74HC595 that connect serially
        :param init_values: a list of 0 or 1 that determine initial value for parallel pins
        :exception input check: serial,register_clock,storage_register_clock must be an instance of machine.Pin or
        pinId(int)
        """
        # init pins
        self.__serial = machine.Pin(serial, mode=machine.Pin.OUT)
        self.__serial.off()
        self.__register_clock = machine.Pin(storage_register_clock, mode=machine.Pin.OUT)
        self.__register_clock.off()
        self.__storage_register_clock = machine.Pin(register_clock, mode=machine.Pin.OUT)
        self.__storage_register_clock.off()
        # determine number of pins and set initial values
        self.__ic_count = ic_count
        self.__pins = ic_count * 8
        if init_values is None:
            self.__values = [0 for _ in range(ic_count * 8)]
        else:
            self.__values = init_values
        self.set_values(self.__values)

    def set_values(self, values: list, commit=True) -> None:
        """give a list of 0 or 1 values and set to pins

        :param commit: when False, commit with :commit(), when True, commit immediately
        :param values: a list of 0 or 1 values. the list may be reverse.
        :return:
        :exception input size of values: size of values not checked in this version.

        values bit banging from first to end to serial pin with clocking on register clock pin.
        frequency of bit banging is about 500kHz.
        at the end, one pulse sent to storage register clock to set the changed values to output.
        """
        self.__values = values
        if commit:
            self.commit()

    def commit(self) -> None:
        """commit the values

        :return:
        """
        # bit banging data
        for data in self.__values:
            self.__serial.value(data)
            self.__storage_register_clock.on()
            t.sleep_us(100)
            self.__storage_register_clock.off()
            t.sleep_us(100)
        # set changed data t0o outputs
        self.__register_clock.on()
        t.sleep_us(100)
        self.__register_clock.off()
        t.sleep_us(100)

    def set_pin(self, index: int, value: int, commit=True) -> None:
        """set a pin status.

        :param commit: when False, commit with :commit(), when True, commit immediately
        :param index: index of pin. start from 0.
        :param value: 0 or 1
        :return:

        change list of last status of values and use methode set_value to set new value of the pin, so all data will
        send again.
        """
        # change list of last status of values
        self.__values[index] = value
        # set new list of values to outputs
        self.set_values(self.__values, commit)

    @property
    def ic_count(self) -> int:
        """return number of 74HC565 ic

        :return: number of 74HC565 ic
        """
        return self.__ic_count

    @property
    def pins_count(self) -> int:
        """return number of controllable pins

        :return: number of controllable pins
        """
        return self.ic_count * 8

    def set_ic_count(self, ic_count: int) -> None:
        """change ic count and number of controllable pins

        this property have not any effect on methods and just is like a hint in this version

        :param ic_count: number of ic 74HC565
        :return:
        """
        self.__ic_count = ic_count
        self.__pins = ic_count * 8


class ParallelToSerial:
    """for read infinity pins as digital input by 3 wire and ic 74HC165.

    this class use for driving ic 74HC165.
    datasheet: https://www.ti.com/lit/gpn/sn74hc165 .
    used for reading infinity pins as digital high impedance inputs by 3 wire.
    interrupt pin can used for handle button inputs that are pull down and one of them raise suddenly as flow the
    schematic circuit below. changing or disabling interrupt not developed in this version.

    Methods:
        ParallelToSerial: construct an instance by giving 3 pins and number of ic 74HC165
        set_ic_count: change ic count and number of readable pins
        value: read the state of a pin

    Properties:
        values: pin states
        ic_count: number of 74HC165 ic
        pins_count: number of readable pins

    Examples:
        from parallel_to_serial import ParallelToSerial
        shift = 12
        serial = 13
        clock = 14
        ic165 = 3
        interrupt =2
        inputs = ParallelToSerial(shift,serial,clock,ic165)

        example1:
        print(inputs.values)

    74HC165 pin map:
        PIN1 : SH/~LD,
        PIN2 : CLK,
        PIN3 : E,
        PIN4 : F,
        PIN5 : G,
        PIN6 : H,
        PIN7 : ~QH,
        PIN8 : GND,
        PIN9 : QH,
        PIN10 : SER,
        PIN11 : A,
        PIN12 : B,
        PIN13 : C,
        PIN14 : D,
        PIN15 : CLK INH,
        PIN16 : Vcc.

    circuit schematic:
          ┌────165────┐
        ──┤A       Vcc├──TO Vcc
          │           │
        ──┤B       CLK├──TO CLOCK PIN
          │           │
        ──┤C   CLK INH├──TO GND
          │           │
        ──┤D        QH├──TO SERIAL PIN
          │           │
        ──┤E       SER├────────────────────────┐
          │           │                        │
        ──┤F    SH/~LD├──TO SHIFT OR LOAD PIN  │
          │           │                        │
        ──┤G       ~QH├──NOT CONNECT           │
          │           │                        │
        ──┤H       GND├──TO GND                │
          └───────────┘                        │
                                               │
          ┌────165────┐                        │
        ──┤A       Vcc├──TO Vcc                │
          │           │                        │
        ──┤B       CLK├──TO CLOCK PIN          │
          │           │                        │
        ──┤C   CLK INH├──TO GND                │
          │           │                        │
        ──┤D        QH├────────────────────────┘
          │           │
        ──┤E       SER├────────────────────────┐
          │           │                        │
        ──┤F    SH/~LD├──TO SHIFT OR LOAD PIN  │
          │           │                        │
        ──┤G       ~QH├──NOT CONNECT           │
          │           │                        │
        ──┤H       GND├──TO GND                │
          └───────────┘                        │
                .                              .
                .                              .
                .                              .
          ┌────165────┐                        │
        ──┤A       Vcc├──TO Vcc                │
          │           │                        │
        ──┤B       CLK├──TO CLOCK PIN          │
          │           │                        │
        ──┤C   CLK INH├──TO GND                │
          │           │                        │
        ──┤D        QH├────────────────────────┘
          │           │
        ──┤E       SER├──TO GND
          │           │
        ──┤F    SH/~LD├──TO SHIFT OR LOAD PIN
          │           │
        ──┤G       ~QH├──NOT CONNECT
          │           │
        ──┤H       GND├──TO GND
          └───────────┘

        A1──►───┐
        B1──►───┤
        .       │
        .       │
        .       │
        Hn──►───┤
                │
                ├──EXTERNAL PULL DOWN WITH 10K
                │
                └──TO INTERRUPT PIN

    """

    def __init__(self, shift: int, serial: int, clock: int, ic_count: int = 1, interrupt_pin: int = None,
                 interrupt_trigger: int = machine.Pin.IRQ_RISING,
                 interrupt_handler: Callable[[machine.Pin], Any] = None):
        """construct an instance of ParallelToSerial and initiate pins

        :param shift: shift or load pin id that connected to pin 1 of ic 74HC165 (SH/~LD)
        :param serial: serial pin id that connected to pin 9 of ic 74HC165 (QH)
        :param clock: clock pin id that connected to pin 2 of ic 74HC165 (CLK)
        :param ic_count: the number of ic 74HC165 that connect serially
        :param interrupt_pin: interrupt pin id
        :param interrupt_trigger: interrupt trigger mode
        :param interrupt_handler: callable function with one input parameter that refer to interrupt pin
        """
        # init pins
        self.__shift = machine.Pin(shift, mode=machine.Pin.OUT, value=1)
        self.__serial = machine.Pin(serial, mode=machine.Pin.IN)
        self.__clock = machine.Pin(clock, mode=machine.Pin.OUT, value=1)
        # set interrupt
        if interrupt_pin is not None:
            self.__interrupt = machine.Pin(interrupt_pin, mode=machine.Pin.IN)
            if interrupt_handler is not None:
                self.__interrupt.irq(trigger=interrupt_trigger, handler=interrupt_handler)
        else:
            self.__interrupt = None
        # determine number of pins and set initial values
        self.__ic_count = ic_count
        self.__pins = ic_count * 8
        self.__values = [0 for _ in range(ic_count * 8)]

    @property
    def values(self) -> list:
        """read all pin states and return a list of states

        raed frequency is about 500kHz.
        reset shift time is about 3 micro seconds.
        returned list may be reverse.

        :return: pin states
        """
        # reset shift to first pin
        t.sleep_ms(1)
        self.__shift.value(0)
        t.sleep_ms(1)
        self.__shift.value(1)
        t.sleep_ms(1)
        # clock and read serial of pins states
        for i in range(self.__pins):
            self.__values[i] = self.__serial.value()
            t.sleep_ms(1)
            self.__clock.value(0)
            t.sleep_ms(1)
            self.__clock(1)
            t.sleep_ms(1)
        return self.__values

    def value(self, index: int) -> int:
        """ return the state of a pin by give pin index

        this function read and update all values by calling values and return state of special pin state.

        :param index: index of pin. start from 0.
        :return: state of pin. 0 or 1.
        """
        return self.values[index]

    @property
    def ic_count(self) -> int:
        """return number of 74HC165 ic

        :return: number of 74HC165 ic
        """
        return self.__ic_count

    @property
    def pins_count(self):
        """return number of readable pins

        :return: number of readable pins
        """
        return self.__pins


class Led:
    """model of LED on a output pin in ic 74HC565

    Methode:
        Led: construct an instance of Led
        on: turn LED on
        off: turn LED off
        set_value: change state of LED on or off
        commit: commit the values

    Properties:
        value: return state of LED

    Examples:
        from serial_to_parallel import SerialToParallel
        from led import Led
        serial = 5
        clock = 4
        storage_clock = 0
        ic565 = 3
        led_index = 0
        outputs = SerialToParallel(serial,clock,storage_clock,ic565)
        led = Led(outputs,led_index)

        example1:
        led.on()

        example2:
        led.off()

        example3:
        import time
        for _ in range(1000):
            led.set_value(1)
            time.sleep_ms(100)
            led.set_value(0)
            time.sleep_ms(100)
    """

    def __init__(self, serial_to_parallel: SerialToParallel, pin_index: int, init_value: int = 0):
        """construct an instance of Led

        :param serial_to_parallel: for connect to led by 74HC565
        :param pin_index: index of LED in serial_to_parallel object. start from 0.
        :param init_value: initial LED state. 0 for off and 1 for on
        """
        self.__serial_to_parallel = serial_to_parallel
        self.__pin_index = pin_index
        self.set_value(init_value)
        self.__value = init_value

    def on(self, commit=True) -> None:
        """ turn LED on

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__serial_to_parallel.set_pin(index=self.__pin_index, value=1, commit=commit)
        self.__value = 1

    def off(self, commit=True) -> None:
        """turn LED off

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__serial_to_parallel.set_pin(index=self.__pin_index, value=0, commit=commit)
        self.__value = 0

    def set_value(self, value: int, commit=True) -> None:
        """change state of LED on or off

        :param commit: when False, commit with :commit(), when True, commit immediately
        :param value: 0 for off and 1 for on
        :return:
        """
        self.__serial_to_parallel.set_pin(index=self.__pin_index, value=value, commit=commit)
        self.__value = value

    def commit(self) -> None:
        """commit the values

        :return:
        """
        self.__serial_to_parallel.commit()

    def value(self) -> int:
        """return the state of LED

        :return: state of LED
        """
        return self.__value


class LedPwm(Led):
    """model of LED with controllable light density by PWM on a output pin in ic 74HC565

    Methods:
        LedPwm: construct LedPwm instance. inheritance from Led. with control of led light density.
        set_light_density: change light density.
        set_pwm_frequency: change pwm frequency of LED.

    Properties:

    Examples:
        from serial_to_parallel import SerialToParallel
        from led_pwm import LedPwm
        serial = 5
        clock = 4
        storage_clock = 0
        ic565 = 3
        led_index = 0
        pwm_pin = 2
        outputs = SerialToParallel(serial,clock,storage_clock,ic565)
        led = LedPwm(outputs,led_index,pwm_pin)

        example1:
        led.set_light_density(512)
        led.on()

        example2:
        import time
        led.on()
        for _ in range(10):
            for i in range(1023):
                led.set_light_density(i)
                time.sleep_ms(5)

    """

    def __init__(self, serial_to_parallel: SerialToParallel, pin_index: int, pwm_pin: int, init_value: int = 0,
                 pwm_duty: int = 0, pwm_frequency: int = 1000):
        """construct LedPwm instance . inheritance from Led. with control of led light density.

        :param serial_to_parallel: for connect to led by 74HC565
        :param pin_index: index of LED in serial_to_parallel object. start from 0.
        :param pwm_pin: pwm pin id for controlling light density
        :param init_value: initial LED state. 0 for off and 1 for on
        :param pwm_duty: initial light density form  0 to 1023 inclusive
        :param pwm_frequency: initial pwm frequency of LED
        """
        super().__init__(serial_to_parallel, pin_index, init_value)
        self.__pwm_pin = machine.Pin(pwm_pin, mode=machine.Pin.OUT)
        self.__pwm_pin.off()
        self.__pwm = machine.PWM(self.__pwm_pin)
        self.__pwm.freq(pwm_frequency)
        self.__pwm.duty(pwm_duty)

    def set_light_density(self, pwm_duty: int) -> None:
        """change light density form  0 to 1023 inclusive.

        :param pwm_duty: from 0 to 1023 inclusive.
        :return:
        """
        self.__pwm.duty(pwm_duty)

    def set_pwm_frequency(self, pwm_frequency: int) -> None:
        """change pwm frequency of LED

        :param pwm_frequency: new frequency
        :return:
        """
        self.__pwm.freq(pwm_frequency)


class ProgressLed:
    """model of progress Led bar connected to output pins of ic 74HC565

    Methode:
        ProgressLed: construct an instance of ProgressLed
        set_value: change progress value
        commit: commit the values
        increase: increase progress value
        decrease: decrease progress value

    Properties:
        value: return progress value

    Examples:
        from serial_to_parallel import SerialToParallel
        from progress_led import ProgressLed
        serial = 5
        clock = 4
        storage_clock = 0
        ic565 = 3
        outputs = SerialToParallel(serial,storage_clock,clock,ic565)
        progress = ProgressLed(outputs,[i for i in range(0,8)])

        example1:
        progress.set_value(2)

        example2:
        import time
        for _ in range(5):
            for __ in range(8):
                progress.increase()
                time.sleep(1)
            for __ in range(8):
                progress.decrease()
                time.sleep(1)
    """

    def __init__(self, serial_to_parallel: SerialToParallel, indexes: list, init_value: int = 0):
        """ construct a instance of progress Led bar.

        :param serial_to_parallel: for connect to led by 74HC565
        :param indexes: a list of ordered pin indexes. start from 0.
        :param init_value: initial progress value
        """
        self.__serial_to_parallel = serial_to_parallel
        self.__LEDs = []
        for led_index in indexes:
            self.__LEDs.append(Led(serial_to_parallel, led_index, 0))
        for i in range(init_value):
            self.__LEDs[i].on(commit=False)
        self.__serial_to_parallel.commit()
        self.__value = init_value

    def set_value(self, value: int, commit=True):
        """change progress value

        :param commit: when False, commit with :commit(), when True, commit immediately
        :param value: new progress value
        :return:
        """
        for i in range(len(self.__LEDs)):
            if i < value:
                self.__LEDs[i].on(commit=False)
            else:
                self.__LEDs[i].off(commit=False)
        if commit:
            self.commit()
        self.__value = value

    def commit(self) -> None:
        """commit the values

        :return:
        """
        self.__serial_to_parallel.commit()

    @property
    def value(self) -> int:
        """return progress value

        :return: progress value
        """
        return self.__value

    def increase(self, commit=True) -> None:
        """increase progress value

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        if self.__value < len(self.__LEDs):
            self.set_value(self.__value + 1, commit=commit)

    def decrease(self, commit=True) -> None:
        """decrease progress value

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        if self.__value > 0:
            self.set_value(self.__value - 1, commit=commit)


class ProgressLedPwm(ProgressLed):
    """model of progress Led bar connected to output pins of ic 74HC565 with controllable light intensity.

    Methode:
        ProgressLedPwm: constructor for ProgressLedPwm
        set_frequency: change pwm frequency of LEDs
        set_light_density: change light density form  0 to 1023 inclusive.

    Properties:

    Examples:
        from serial_to_parallel import SerialToParallel
        from progress_led_pwm import ProgressLedPwm
        serial = 5
        clock = 4
        storage_clock = 0
        ic565 = 3
        pwm_pin = 2
        outputs = SerialToParallel(serial,storage_clock,clock,ic565)
        progress_pwm = ProgressLedPwm(outputs,[i for i in range(0,8)],pwm_pin)

        example1:
        import time
        for _ in range(5):
            for __ in range(8):
                progress_pwm.increase()
                progress_pwm.set_light_density(int(125*progress_pwm.value))
                time.sleep(1)
            for __ in range(8):
                progress_pwm.decrease()
                progress_pwm.set_light_density(int(125*progress_pwm.value))
                time.sleep(1)

    """

    def __init__(self, serial_to_parallel: SerialToParallel, indexes: list, pwm_pin: int, init_light_density: int = 0,
                 init_frequency: int = 1000):
        """ construct a instance of progress Led bar.inheritance from ProgressLed. with control of LEDs light density.

        :param serial_to_parallel: for connect to led by 74HC565
        :param indexes: a list of ordered pin indexes. start from 0.
        :param pwm_pin: initial light density form  0 to 1023 inclusive
        :param init_frequency: initial pwm frequency of LEDs
        """
        super().__init__(serial_to_parallel, indexes)
        self.__pwm = machine.PWM(machine.Pin(pwm_pin, mode=machine.Pin.OUT))
        self.__pwm.freq(init_frequency)
        self.__pwm.duty(init_light_density)

    def set_frequency(self, frequency: int) -> None:
        """change pwm frequency of LEDs

        :param frequency: new frequency
        :return:
        """
        self.__pwm.freq(frequency)

    def set_light_density(self, pwm_duty: int) -> None:
        """change light density form  0 to 1023 inclusive.

        :param pwm_duty: from 0 to 1023 inclusive.
        :return:
        """
        self.__pwm.duty(pwm_duty)


class RGB:
    """model of RGB LED with controllable light color and density by PWM on red, green and blue outputs in ic 74HC565 .

    Methods:
        RGB: construct an instance of RGB class.
        set_rgb: change color and light density.
        set_frequency: change pwm frequency.

    Properties:
        red: red led
        blue: blue led
        green: green led

    Examples:

    """

    def __init__(self, serial_to_parallel: SerialToParallel, red_pin_index: int, green_pin_index: int,
                 blue_pin_index: int, red_pwm_pin: int, green_pwm_pin: int, blue_pwm_pin: int, red_value: int = 0,
                 green_value: int = 0, blue_value: int = 0, pwm_frequency: int = 1000):
        """construct an instance of RGB class. include 3 LedPwm for red and green and blue LED.

        :param serial_to_parallel: for connect to LEDs by 74HC565
        :param red_pin_index: index of red LED in serial_to_parallel object. start from 0.
        :param green_pin_index: index of green LED in serial_to_parallel object. start from 0.
        :param blue_pin_index: index of blue LED in serial_to_parallel object. start from 0.
        :param red_pwm_pin: pwm red pin id for controlling red light density
        :param green_pwm_pin: pwm green pin id for controlling green light density
        :param blue_pwm_pin: pwm blue pin id for controlling blue light density
        :param red_value: initial red value in range of 0 to 65535 inclusive
        :param green_value: initial green value in range of 0 to 65535 inclusive
        :param blue_value: initial blue value in range of 0 to 65535 inclusive
        :param pwm_frequency: initial pwm frequency for red and green and blue LEDs
        """
        self.__red = LedPwm(serial_to_parallel=serial_to_parallel, pin_index=red_pin_index, pwm_pin=red_pwm_pin,
                            init_value=1, pwm_duty=red_value, pwm_frequency=pwm_frequency)
        self.__green = LedPwm(serial_to_parallel=serial_to_parallel, pin_index=green_pin_index, pwm_pin=green_pwm_pin,
                              init_value=1, pwm_duty=green_value, pwm_frequency=pwm_frequency)
        self.__blue = LedPwm(serial_to_parallel=serial_to_parallel, pin_index=blue_pin_index, pwm_pin=blue_pwm_pin,
                             init_value=1, pwm_duty=blue_value, pwm_frequency=pwm_frequency)
        self.__serial_to_parallel = serial_to_parallel

    def set_rgb(self, r: int, g: int, b: int) -> None:
        """ change color and light density by determine red and green and blue value in range of 0 to 65535 inclusive

        :param r: red value in range of 0 to 65535 inclusive
        :param g: green value in range of 0 to 65535 inclusive
        :param b: blue value in range of 0 to 65535 inclusive
        :return:
        """
        self.__red.set_light_density(r)
        self.__green.set_light_density(g)
        self.__blue.set_light_density(b)

    def set_frequency(self, frequency: int) -> None:
        """change pwm frequency of red and green and blue led

        :param frequency: new frequency
        :return:
        """
        self.__red.set_pwm_frequency(frequency)
        self.__green.set_pwm_frequency(frequency)
        self.__blue.set_pwm_frequency(frequency)

    @property
    def red(self) -> LedPwm:
        """ return red led as a readonly object

        :return: red led
        """
        return self.__red

    @property
    def blue(self) -> LedPwm:
        """return blue led as a readonly object

        :return: blue led
        """
        return self.__blue

    @property
    def green(self) -> LedPwm:
        """return green led as a readonly object

        :return: green led
        """
        return self.__green


class SevenSegment:
    """model of one digit seven segment common anode that connected to output pins of ic 74HC565

    Methods:
        SevenSegment: construct an instance of SevenSegment.
        commit: commit the values
        off: turn off all LEDs on seven segment
        zero: show 0 on seven segment
        one: show 1 on seven segment
        two: show 2 on seven segment
        three: show 3 on seven segment
        four: show 4 on seven segment
        five: show 5 on seven segment
        six: show 6 on seven segment
        seven: show 7 on seven segment
        eight: show 8 on seven segment
        nine: show 9 on seven segment
        A: show A on seven segment
        B: show b on seven segment
        C: show C or c on seven segment
        D: show d on seven segment
        E: show E on seven segment
        F: show F on seven segment
        G: show G or g on seven segment
        H: show H or h on seven segment
        I: show I on seven segment
        J: show J on seven segment
        L: show L on seven segment
        N: show n on seven segment
        O: show O or o on seven segment
        P: show P on seven segment
        Q: show q on seven segment
        R: show r on seven segment
        S: show S on seven segment
        T: show t on seven segment
        U: show U or u on seven segment
        Y: show y on seven segment
        Z: show Z on seven segment
        set_value: show a number in range 0 to 9 inclusive on seven segment

    Properties:
        a: a led
        b: b led
        c: c led
        d: d led
        e: e led
        f: f led
        g: g led
        dot: dot led

    Examples:
        from serial_to_parallel import SerialToParallel
        from seven_segment import SevenSegment
        serial = 5
        clock = 4
        storage_clock = 0
        ic565 = 3
        outputs = SerialToParallel(serial,storage_clock,clock,ic565)
        dp = 0
        c = 1
        d = 2
        e = 3
        g = 4
        f = 5
        a = 6
        b = 7
        segment = SevenSegment(outputs,a,b,c,d,e,f,g,dp)

        example1:
        import time
        for _ in range(20):
            for i in range(10):
                segment.set_value(i)
                time.sleep(1)

        example2:
        segment.H(uppercase=False)
    """

    def __init__(self, serial_to_parallel: SerialToParallel, a_pin_index: int, b_pin_index: int, c_pin_index: int,
                 d_pin_index: int, e_pin_index: int, f_pin_index: int, g_pin_index: int, dot_pin_index: int):
        """construct an instance of SevenSegment class include 8 led.

        :param serial_to_parallel: for connect to LEDs by 74HC565
        :param a_pin_index: index of A LED in serial_to_parallel object connected to QB. start from 0.
        :param b_pin_index: index of B LED in serial_to_parallel object connected to QA. start from 0.
        :param c_pin_index: index of C LED in serial_to_parallel object connected to QH. start from 0.
        :param d_pin_index: index of D LED in serial_to_parallel object connected to QF. start from 0.
        :param e_pin_index: index of E LED in serial_to_parallel object connected to QE. start from 0.
        :param f_pin_index: index of F LED in serial_to_parallel object connected to QC. start from 0.
        :param g_pin_index: index of G LED in serial_to_parallel object connected to QD. start from 0.
        :param dot_pin_index: index of DOT LED in serial_to_parallel object connected to QG. start from 0.
        """
        self.__a = Led(serial_to_parallel=serial_to_parallel, pin_index=a_pin_index, init_value=1)
        self.__b = Led(serial_to_parallel=serial_to_parallel, pin_index=b_pin_index, init_value=1)
        self.__c = Led(serial_to_parallel=serial_to_parallel, pin_index=c_pin_index, init_value=1)
        self.__d = Led(serial_to_parallel=serial_to_parallel, pin_index=d_pin_index, init_value=1)
        self.__e = Led(serial_to_parallel=serial_to_parallel, pin_index=e_pin_index, init_value=1)
        self.__f = Led(serial_to_parallel=serial_to_parallel, pin_index=f_pin_index, init_value=1)
        self.__g = Led(serial_to_parallel=serial_to_parallel, pin_index=g_pin_index, init_value=1)
        self.__dot = Led(serial_to_parallel=serial_to_parallel, pin_index=dot_pin_index, init_value=1)
        self.__serial_to_parallel = serial_to_parallel

    @property
    def a(self) -> Led:
        """return a led as readonly object

        :return: a led
        """
        return self.__a

    @property
    def b(self) -> Led:
        """return b led as readonly object

        :return: b led
        """
        return self.__b

    @property
    def c(self) -> Led:
        """return c led as readonly object

        :return: c led
        """
        return self.__c

    @property
    def d(self) -> Led:
        """return d led as readonly object

        :return: d led
        """
        return self.__d

    @property
    def e(self) -> Led:
        """return e led as readonly object

        :return: e led
        """
        return self.__e

    @property
    def f(self) -> Led:
        """return f led as readonly object

        :return: f led
        """
        return self.__f

    @property
    def g(self) -> Led:
        """return g led as readonly object

        :return: g led
        """
        return self.__g

    @property
    def dot(self) -> Led:
        """ return dot led as readonly object

        :return: dot led
        """
        return self.__dot

    def commit(self) -> None:
        """commit the values

        :return:
        """
        self.__serial_to_parallel.commit()

    def off(self, commit=True) -> None:
        """turn off all LEDs on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.off(commit=False)
        self.__b.off(commit=False)
        self.__c.off(commit=False)
        self.__d.off(commit=False)
        self.__e.off(commit=False)
        self.__f.off(commit=False)
        self.__g.off(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def zero(self, commit=True) -> None:
        """show 0 on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.on(commit=False)
        self.__c.on(commit=False)
        self.__d.on(commit=False)
        self.__e.on(commit=False)
        self.__f.on(commit=False)
        self.__g.off(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def one(self, commit=False) -> None:
        """show 1 on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.off(commit=False)
        self.__b.on(commit=False)
        self.__c.on(commit=False)
        self.__d.off(commit=False)
        self.__e.off(commit=False)
        self.__f.off(commit=False)
        self.__g.off(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def two(self, commit=True) -> None:
        """show 2 on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.on(commit=False)
        self.__c.off(commit=False)
        self.__d.on(commit=False)
        self.__e.on(commit=False)
        self.__f.off(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def three(self, commit=True) -> None:
        """show 3 on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.on(commit=False)
        self.__c.on(commit=False)
        self.__d.on(commit=False)
        self.__e.off(commit=False)
        self.__f.off(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def four(self, commit=True) -> None:
        """show 4 on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.off(commit=False)
        self.__b.on(commit=False)
        self.__c.on(commit=False)
        self.__d.off(commit=False)
        self.__e.off(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def five(self, commit=True) -> None:
        """show 5 on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.off(commit=False)
        self.__c.on(commit=False)
        self.__d.on(commit=False)
        self.__e.off(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def six(self, commit=True) -> None:
        """show 6 on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.off(commit=False)
        self.__c.on(commit=False)
        self.__d.on(commit=False)
        self.__e.on(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def seven(self, commit=True) -> None:
        """show 7 on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.on(commit=False)
        self.__c.on(commit=False)
        self.__d.off(commit=False)
        self.__e.off(commit=False)
        self.__f.off(commit=False)
        self.__g.off(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def eight(self, commit=True) -> None:
        """show 8 on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.on(commit=False)
        self.__c.on(commit=False)
        self.__d.on(commit=False)
        self.__e.on(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def nine(self, commit=True) -> None:
        """show 9 on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.on(commit=False)
        self.__c.on(commit=False)
        self.__d.on(commit=False)
        self.__e.off(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def A(self, commit=True) -> None:
        """show A on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.on(commit=False)
        self.__c.on(commit=False)
        self.__d.off(commit=False)
        self.__e.on(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def B(self, commit=True) -> None:
        """show B on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.off(commit=False)
        self.__b.off(commit=False)
        self.__c.on(commit=False)
        self.__d.on(commit=False)
        self.__e.on(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def C(self, uppercase=True, commit=True) -> None:
        """ show C or c on seven segment

        :param uppercase: Enter True for C and False for c
        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        if uppercase:
            self.__a.on(commit=False)
            self.__b.off(commit=False)
            self.__c.off(commit=False)
            self.__d.on(commit=False)
            self.__e.on(commit=False)
            self.__f.on(commit=False)
            self.__g.off(commit=False)
            self.__dot.off(commit=False)
        else:
            self.__a.off(commit=False)
            self.__b.off(commit=False)
            self.__c.off(commit=False)
            self.__d.on(commit=False)
            self.__e.on(commit=False)
            self.__f.off(commit=False)
            self.__g.on(commit=False)
            self.__dot.off(commit=False)
        if commit:
            self.commit()

    def D(self, commit=True) -> None:
        """show D on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.off(commit=False)
        self.__b.on(commit=False)
        self.__c.on(commit=False)
        self.__d.on(commit=False)
        self.__e.on(commit=False)
        self.__f.off(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def E(self, commit=True) -> None:
        """show E on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.off(commit=False)
        self.__c.off(commit=False)
        self.__d.on(commit=False)
        self.__e.on(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def F(self, commit=True) -> None:
        """show F on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.off(commit=False)
        self.__c.off(commit=False)
        self.__d.off(commit=False)
        self.__e.on(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def G(self, uppercase=True, commit=True) -> None:
        """ show G or g on seven segment

        :param uppercase: Enter True for G and False for g
        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        if uppercase:
            self.__a.on(commit=False)
            self.__b.off(commit=False)
            self.__c.on(commit=False)
            self.__d.on(commit=False)
            self.__e.on(commit=False)
            self.__f.on(commit=False)
            self.__g.off(commit=False)
            self.__dot.off(commit=False)
        else:
            self.__a.on(commit=False)
            self.__b.on(commit=False)
            self.__c.on(commit=False)
            self.__d.on(commit=False)
            self.__e.off(commit=False)
            self.__f.on(commit=False)
            self.__g.on(commit=False)
            self.__dot.off(commit=False)
        if commit:
            self.commit()

    def H(self, uppercase=True, commit=True) -> None:
        """ show H or h on seven segment

        :param uppercase: Enter True for H and False for h
        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        if uppercase:
            self.__a.off(commit=False)
            self.__b.on(commit=False)
            self.__c.on(commit=False)
            self.__d.off(commit=False)
            self.__e.on(commit=False)
            self.__f.on(commit=False)
            self.__g.on(commit=False)
            self.__dot.off(commit=False)
        else:
            self.__a.off(commit=False)
            self.__b.off(commit=False)
            self.__c.on(commit=False)
            self.__d.off(commit=False)
            self.__e.on(commit=False)
            self.__f.on(commit=False)
            self.__g.on(commit=False)
            self.__dot.off(commit=False)
        if commit:
            self.commit()

    def I(self, commit=True) -> None:
        """show I on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.off(commit=False)
        self.__b.on(commit=False)
        self.__c.on(commit=False)
        self.__d.off(commit=False)
        self.__e.off(commit=False)
        self.__f.off(commit=False)
        self.__g.off(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def J(self, commit=True) -> None:
        """show J on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.off(commit=False)
        self.__b.on(commit=False)
        self.__c.on(commit=False)
        self.__d.on(commit=False)
        self.__e.off(commit=False)
        self.__f.off(commit=False)
        self.__g.off(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def L(self, commit=True) -> None:
        """show L on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.off(commit=False)
        self.__b.off(commit=False)
        self.__c.off(commit=False)
        self.__d.on(commit=False)
        self.__e.on(commit=False)
        self.__f.on(commit=False)
        self.__g.off(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def N(self, commit=True) -> None:
        """show n on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.off(commit=False)
        self.__b.off(commit=False)
        self.__c.on(commit=False)
        self.__d.off(commit=False)
        self.__e.on(commit=False)
        self.__f.off(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def O(self, uppercase=True, commit=True) -> None:
        """ show O or o on seven segment

        :param uppercase: Enter True for O and False for o
        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        if uppercase:
            self.__a.on(commit=False)
            self.__b.on(commit=False)
            self.__c.on(commit=False)
            self.__d.on(commit=False)
            self.__e.on(commit=False)
            self.__f.on(commit=False)
            self.__g.off(commit=False)
            self.__dot.off(commit=False)
        else:
            self.__a.off(commit=False)
            self.__b.off(commit=False)
            self.__c.on(commit=False)
            self.__d.on(commit=False)
            self.__e.on(commit=False)
            self.__f.off(commit=False)
            self.__g.on(commit=False)
            self.__dot.off(commit=False)
        if commit:
            self.commit()

    def P(self, commit=True) -> None:
        """show P on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.on(commit=False)
        self.__c.off(commit=False)
        self.__d.off(commit=False)
        self.__e.on(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def Q(self, commit=True) -> None:
        """show Q on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.on(commit=False)
        self.__c.on(commit=False)
        self.__d.off(commit=False)
        self.__e.off(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def R(self, commit=True) -> None:
        """show R on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.off(commit=False)
        self.__b.off(commit=False)
        self.__c.off(commit=False)
        self.__d.off(commit=False)
        self.__e.on(commit=False)
        self.__f.off(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def S(self, commit=True) -> None:
        """show S on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.off(commit=False)
        self.__c.on(commit=False)
        self.__d.on(commit=False)
        self.__e.off(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def T(self, commit=True) -> None:
        """show T on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.off(commit=False)
        self.__b.off(commit=False)
        self.__c.off(commit=False)
        self.__d.on(commit=False)
        self.__e.on(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def U(self, uppercase=True, commit=True) -> None:
        """ show U or u on seven segment

        :param uppercase: Enter True for U and False for u
        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        if uppercase:
            self.__a.off(commit=False)
            self.__b.on(commit=False)
            self.__c.on(commit=False)
            self.__d.on(commit=False)
            self.__e.on(commit=False)
            self.__f.on(commit=False)
            self.__g.off(commit=False)
            self.__dot.off(commit=False)
        else:
            self.__a.off(commit=False)
            self.__b.off(commit=False)
            self.__c.on(commit=False)
            self.__d.on(commit=False)
            self.__e.on(commit=False)
            self.__f.off(commit=False)
            self.__g.off(commit=False)
            self.__dot.off(commit=False)
        if commit:
            self.commit()

    def Y(self, commit=True) -> None:
        """show Y on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.off(commit=False)
        self.__b.on(commit=False)
        self.__c.on(commit=False)
        self.__d.on(commit=False)
        self.__e.off(commit=False)
        self.__f.on(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def Z(self, commit=True) -> None:
        """show Z on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        self.__a.on(commit=False)
        self.__b.on(commit=False)
        self.__c.off(commit=False)
        self.__d.on(commit=False)
        self.__e.on(commit=False)
        self.__f.off(commit=False)
        self.__g.on(commit=False)
        self.__dot.off(commit=False)
        if commit:
            self.commit()

    def set_value(self, value: int, commit=True) -> None:
        """show a number in range 0 to 9 inclusive on seven segment

        :param commit: when False, commit with :commit(), when True, commit immediately
        :param value: a number in range 0 to 9 inclusive
        :return:
        """
        if value == 0:
            self.zero(commit=commit)
        elif value == 1:
            self.one(commit=commit)
        elif value == 2:
            self.two(commit=commit)
        elif value == 3:
            self.three(commit=commit)
        elif value == 4:
            self.four(commit=commit)
        elif value == 5:
            self.five(commit=commit)
        elif value == 6:
            self.six(commit=commit)
        elif value == 7:
            self.seven(commit=commit)
        elif value == 8:
            self.eight(commit=commit)
        elif value == 9:
            self.nine(commit=commit)


class MultiSevenSegment:
    """model of multi one digit seven segment common anode that are connected to output pins of ic 74HC565.

    Methods:
        MultiSevenSegment: construct an instance of MultiSevenSegment
        commit: commit the values
        set_value: show integer positive number on seven segments
        off: turn off all seven segments
        set_word: show a word with specific character of A,B,C,D,E,F,G,H,I,J,L,N,O,P,Q,R,S,T,U,Y,Z
        show_time:show time in format HHMM

    Properties:
        seven_segments: list of SevenSegment

    Examples:
        from serial_to_parallel import SerialToParallel
        from seven_segment import SevenSegment
        from multi_seven_segment import MultiSevenSegment
        serial = 5
        clock = 4
        storage_clock = 0
        ic565 = 3
        outputs = SerialToParallel(serial,storage_clock,clock,ic565)
        dp1 = 0
        c1 = 1
        d1 = 2
        e1 = 3
        g1 = 4
        f1 = 5
        a1 = 6
        b1 = 7
        seg1 = SevenSegment(outputs,a1,b1,c1,d1,e1,f1,g1,dp1)
        dp2 = 8
        c2 = 9
        d2 = 10
        e2 = 11
        g2 = 12
        f2 = 13
        a2 = 14
        b2 = 15
        seg2 = SevenSegment(outputs,a2,b2,c2,d2,e2,f2,g2,dp2)
        dp3 = 16
        c3 = 17
        d3 = 18
        e3 = 19
        g3 = 20
        f3 = 21
        a3 = 22
        b3 = 23
        seg3 = SevenSegment(outputs,a3,b3,c3,d3,e3,f3,g3,dp3)
        digits = MultiSevenSegment([seg1,seg2,seg3])

        example1:
        import time
        for i in range(999):
            digits.set_value(i)
            time.sleep_ms(100)

        example2:
        digits.set_word("ABC")

        example3:
        digits.show_time(12,30)

    """

    def __init__(self, seven_segments: list[SevenSegment]):
        """construct an instance of MultiSevenSegment .

        :param seven_segments: list of ordered SevenSegment that connected to output pins of ic 74HC565 .
        """
        self.__seven_segments = seven_segments

    @property
    def seven_segments(self) -> list[SevenSegment]:
        """ return a list of SevenSegment. readonly.

        :return: list of SevenSegment
        """
        return self.__seven_segments

    def commit(self) -> None:
        """commit the values

        :return:
        """
        self.__seven_segments[0].commit()

    def set_value(self, value: int, commit=True) -> None:
        """show integer positive number on seven segments

        :param commit: when False, commit with :commit(), when True, commit immediately
        :param value: positive number to show
        :return:
        """
        i = 0
        self.off(commit=False)
        while value > 0:
            self.__seven_segments[i].set_value(int(math.fmod(value, 10)), commit=False)
            value = int(value / 10)
            i = i + 1
        if commit:
            self.commit()

    def off(self, commit=True) -> None:
        """turn off all seven segments

        :param commit: when False, commit with :commit(), when True, commit immediately
        :return:
        """
        for seven_segment in self.__seven_segments:
            seven_segment.off(commit=False)
        if commit:
            self.commit()

    def set_word(self, word: str) -> None:
        """show a word with specific character of A,B,C,D,E,F,G,H,I,J,L,N,O,P,Q,R,S,T,U,Y,Z,0,1,2,3,4,5,6,7,8,9

        :param word: a word with specific character of A,B,C,D,E,F,G,H,I,J,L,N,O,P,Q,R,S,T,U,Y,Z,,0,1,2,3,4,5,6,7,8,9
        :return:
        """
        for i in range(0, len(word)):
            if word[i] == 'A' or word[i] == 'a':
                self.seven_segments[-i - 1].A(commit=False)
            elif word[i] == 'B' or word[i] == 'b':
                self.seven_segments[-i - 1].B(commit=False)
            elif word[i] == 'C':
                self.seven_segments[-i - 1].C(uppercase=True, commit=False)
            elif word[i] == 'c':
                self.seven_segments[-i - 1].C(uppercase=False, commit=False)
            elif word[i] == 'D' or word[i] == 'd':
                self.seven_segments[-i - 1].D(commit=False)
            elif word[i] == 'E' or word[i] == 'e':
                self.seven_segments[-i - 1].E(commit=False)
            elif word[i] == 'F' or word[i] == 'f':
                self.seven_segments[-i - 1].F(commit=False)
            elif word[i] == 'G':
                self.seven_segments[-i - 1].G(uppercase=True, commit=False)
            elif word[i] == 'g':
                self.seven_segments[-i - 1].G(uppercase=False, commit=False)
            elif word[i] == 'H':
                self.seven_segments[-i - 1].H(uppercase=True, commit=False)
            elif word[i] == 'h':
                self.seven_segments[-i - 1].H(uppercase=False, commit=False)
            elif word[i] == 'I' or word[i] == 'i':
                self.seven_segments[-i - 1].I(commit=False)
            elif word[i] == 'J' or word[i] == 'j':
                self.seven_segments[-i - 1].J(commit=False)
            elif word[i] == 'L' or word[i] == 'l':
                self.seven_segments[-i - 1].L(commit=False)
            elif word[i] == 'N' or word[i] == 'n':
                self.seven_segments[-i - 1].N(commit=False)
            elif word[i] == 'O':
                self.seven_segments[-i - 1].O(uppercase=True, commit=False)
            elif word[i] == 'o':
                self.seven_segments[-i - 1].O(uppercase=False, commit=False)
            elif word[i] == 'P' or word[i] == 'p':
                self.seven_segments[-i - 1].P(commit=False)
            elif word[i] == 'Q' or word[i] == 'q':
                self.seven_segments[-i - 1].Q(commit=False)
            elif word[i] == 'R' or word[i] == 'r':
                self.seven_segments[-i - 1].R(commit=False)
            elif word[i] == 'S' or word[i] == 's':
                self.seven_segments[-i - 1].S(commit=False)
            elif word[i] == 'T' or word[i] == 't':
                self.seven_segments[-i - 1].T(commit=False)
            elif word[i] == 'U':
                self.seven_segments[-i - 1].U(uppercase=True, commit=False)
            elif word[i] == 'u':
                self.seven_segments[-i - 1].U(uppercase=False, commit=False)
            elif word[i] == 'Y' or word[i] == 'y':
                self.seven_segments[-i - 1].Y(commit=False)
            elif word[i] == 'Z' or word[i] == 'z':
                self.seven_segments[-i - 1].Z(commit=False)
            elif word[i] == '0':
                self.seven_segments[-i - 1].zero(commit=False)
            elif word[i] == '1':
                self.seven_segments[-i - 1].one(commit=False)
            elif word[i] == '2':
                self.seven_segments[-i - 1].two(commit=False)
            elif word[i] == '3':
                self.seven_segments[-i - 1].three(commit=False)
            elif word[i] == '4':
                self.seven_segments[-i - 1].four(commit=False)
            elif word[i] == '5':
                self.seven_segments[-i - 1].five(commit=False)
            elif word[i] == '6':
                self.seven_segments[-i - 1].six(commit=False)
            elif word[i] == '7':
                self.seven_segments[-i - 1].seven(commit=False)
            elif word[i] == '8':
                self.seven_segments[-i - 1].eight(commit=False)
            elif word[i] == '9':
                self.seven_segments[-i - 1].nine(commit=False)
        self.commit()

    def show_time(self, hour: int, minute: int) -> None:
        """ show time in format HHMM

        :param hour: hour
        :param minute:  minute
        :return:
        """
        self.set_value(hour * 100 + minute)


class Buzzer(Led):
    """model of Buzzer on a output pin in ic 74HC565

        Methods:
            Buzzer: construct Buzzer instance. inheritance from Led.
            beep: buzzer beeped with controllable duration in ms
            double_beep: buzzer beeped twice with controllable duration in ms

        Properties:
            timer: return timer instance

        Examples:
            from serial_to_parallel import SerialToParallel
            from buzzer import Buzzer
            from machine import Timer
            serial = 5
            clock = 4
            storage_clock = 0
            ic565 = 3
            buzzer_index = 0
            outputs = SerialToParallel(serial,clock,storage_clock,ic565)
            timer = Timer(0)
            buzzer = Buzzer(outputs,buzzer_index,timer)

            example1:
            buzzer.beep(300)
            timer.sleep(1000)
            buzzer.double_beep(300,100)

        """

    def __init__(self, serial_to_parallel: SerialToParallel, pin_index: int, timer: Timer):
        """construct Buzzer instance. inheritance from Led.

        :param serial_to_parallel: for connect to LEDs by 74HC565
        :param pin_index: index of LED in serial_to_parallel object. start from 0.
        :param timer: timer instance for control duration of sound. connected to Timer(0) if None
        """
        super().__init__(serial_to_parallel, pin_index)
        if timer is None:
            self.__timer = Timer(0)
        else:
            self.__timer = timer

    def beep(self, duration: int) -> None:
        """buzzer beeped with controllable duration in ms

        :param duration: sound duration in ms
        :return:
        """

        def callback(buzzer: Buzzer) -> None:
            buzzer.off(commit=True)

        self.timer.init(period=duration, mode=Timer.ONE_SHOT, callback=lambda t: callback(self))
        self.on(commit=True)

    def double_beep(self, on_duration: int, off_duration) -> None:
        """buzzer beeped twice with controllable duration in ms

        :param on_duration: sound duration in ms
        :param off_duration: duration between tow sound
        :return:
        """

        def callback(buzzer: Buzzer) -> None:
            buzzer.off(commit=True)
            buzzer.timer.init(period=off_duration, mode=Timer.ONE_SHOT, callback=lambda t: buzzer.beep(on_duration))

        self.timer.init(period=on_duration, mode=Timer.ONE_SHOT, callback=lambda t: callback(self))
        self.on(commit=True)

    @property
    def timer(self):
        """return timer instance

        :return: timer instance
        """
        return self.__timer


class Button:
    """model of button connected to input pins of ic 74HC165
    ******  developing  ******

    Methods:
        Button: construct an instance of Button
        read: read button state

    Properties:

    Examples:

    """

    def __init__(self, parallel_to_serial: ParallelToSerial, pin_index: int):
        """construct an instance of Button

        :param parallel_to_serial: for connect to button by 74HC165
        :param pin_index: index of button in parallel_to_serial object
        """
        self.__parallel_to_serial = parallel_to_serial
        self.__pin_index = pin_index

