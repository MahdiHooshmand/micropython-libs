from serial_to_parallel import SerialToParallel
from led import Led


class SevenSegment:

    def __init__(self, serial_to_parallel: SerialToParallel, a_pin_index: int, b_pin_index: int, c_pin_index: int,
                 d_pin_index: int, e_pin_index: int, f_pin_index: int, g_pin_index: int, dot_pin_index: int):
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
        return self.__a

    @property
    def b(self) -> Led:
        return self.__b

    @property
    def c(self) -> Led:
        return self.__c

    @property
    def d(self) -> Led:
        return self.__d

    @property
    def e(self) -> Led:
        return self.__e

    @property
    def f(self) -> Led:
        return self.__f

    @property
    def g(self) -> Led:
        return self.__g

    @property
    def dot(self) -> Led:
        return self.__dot

    def commit(self) -> None:
        self.__serial_to_parallel.commit()

    def off(self, commit=True) -> None:
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