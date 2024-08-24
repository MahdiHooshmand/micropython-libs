from seven_segment import SevenSegment

import math


class MultiSevenSegment:

    def __init__(self, seven_segments: list[SevenSegment]):
        self.__seven_segments = seven_segments
        self.__last = None

    @property
    def seven_segments(self) -> list[SevenSegment]:
        return self.__seven_segments

    @property
    def last(self):
        return self.__last

    def commit(self) -> None:
        self.__seven_segments[0].commit()

    def set_value(self, value: int, commit=True) -> None:
        if self.__last == value:
            return
        self.__last = value
        i = 0
        self.off(commit=False)
        while value > 0:
            self.__seven_segments[i].set_value(int(math.fmod(value, 10)), commit=False)
            value = int(value / 10)
            i = i + 1
        if commit:
            self.commit()

    def off(self, commit=True) -> None:
        for seven_segment in self.__seven_segments:
            seven_segment.off(commit=False)
        if commit:
            self.commit()

    def set_word(self, word: str) -> None:
        if self.__last == word:
            return
        self.__last = word
        for i in range(0, len(word)):
            if word[i] == 'A' or word[i] == 'a':
                self.seven_segments[-i-1].A(commit=False)
            elif word[i] == 'B' or word[i] == 'b':
                self.seven_segments[-i-1].B(commit=False)
            elif word[i] == 'C':
                self.seven_segments[-i-1].C(uppercase=True, commit=False)
            elif word[i] == 'c':
                self.seven_segments[-i-1].C(uppercase=False, commit=False)
            elif word[i] == 'D' or word[i] == 'd':
                self.seven_segments[-i-1].D(commit=False)
            elif word[i] == 'E' or word[i] == 'e':
                self.seven_segments[-i-1].E(commit=False)
            elif word[i] == 'F' or word[i] == 'f':
                self.seven_segments[-i-1].F(commit=False)
            elif word[i] == 'G':
                self.seven_segments[-i-1].G(uppercase=True, commit=False)
            elif word[i] == 'g':
                self.seven_segments[-i-1].G(uppercase=False, commit=False)
            elif word[i] == 'H':
                self.seven_segments[-i-1].H(uppercase=True, commit=False)
            elif word[i] == 'h':
                self.seven_segments[-i-1].H(uppercase=False, commit=False)
            elif word[i] == 'I' or word[i] == 'i':
                self.seven_segments[-i-1].I(commit=False)
            elif word[i] == 'J' or word[i] == 'j':
                self.seven_segments[-i-1].J(commit=False)
            elif word[i] == 'L' or word[i] == 'l':
                self.seven_segments[-i-1].L(commit=False)
            elif word[i] == 'N' or word[i] == 'n':
                self.seven_segments[-i-1].N(commit=False)
            elif word[i] == 'O':
                self.seven_segments[-i-1].O(uppercase=True, commit=False)
            elif word[i] == 'o':
                self.seven_segments[-i-1].O(uppercase=False, commit=False)
            elif word[i] == 'P' or word[i] == 'p':
                self.seven_segments[-i-1].P(commit=False)
            elif word[i] == 'Q' or word[i] == 'q':
                self.seven_segments[-i-1].Q(commit=False)
            elif word[i] == 'R' or word[i] == 'r':
                self.seven_segments[-i-1].R(commit=False)
            elif word[i] == 'S' or word[i] == 's':
                self.seven_segments[-i-1].S(commit=False)
            elif word[i] == 'T' or word[i] == 't':
                self.seven_segments[-i-1].T(commit=False)
            elif word[i] == 'U':
                self.seven_segments[-i-1].U(uppercase=True, commit=False)
            elif word[i] == 'u':
                self.seven_segments[-i-1].U(uppercase=False, commit=False)
            elif word[i] == 'Y' or word[i] == 'y':
                self.seven_segments[-i-1].Y(commit=False)
            elif word[i] == 'Z' or word[i] == 'z':
                self.seven_segments[-i-1].Z(commit=False)
            elif word[i] == '0':
                self.seven_segments[-i-1].zero(commit=False)
            elif word[i] == '1':
                self.seven_segments[-i-1].one(commit=False)
            elif word[i] == '2':
                self.seven_segments[-i-1].two(commit=False)
            elif word[i] == '3':
                self.seven_segments[-i-1].three(commit=False)
            elif word[i] == '4':
                self.seven_segments[-i-1].four(commit=False)
            elif word[i] == '5':
                self.seven_segments[-i-1].five(commit=False)
            elif word[i] == '6':
                self.seven_segments[-i-1].six(commit=False)
            elif word[i] == '7':
                self.seven_segments[-i-1].seven(commit=False)
            elif word[i] == '8':
                self.seven_segments[-i-1].eight(commit=False)
            elif word[i] == '9':
                self.seven_segments[-i-1].nine(commit=False)
        self.commit()

    def show_time(self, hour: int, minute: int) -> None:
        self.set_value(hour * 100 + minute)
