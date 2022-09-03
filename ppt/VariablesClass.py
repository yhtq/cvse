from abc import ABCMeta
from datetime import datetime
from typing import TypeVar, Optional
import re

color_map: dict[int, tuple[str, str]] = {}
with open('color.txt', 'r', encoding='utf-8') as f:
    for line in f.readlines():
        line = line.strip()
        if line[0] == '#':
            continue
        line = line.split('#')[0]
        if line:
            line = [i.strip() for i in line.split('=')]
            temp_list = [i.strip() for i in line[1].split(',')]
            if len(line) != 2 or len(temp_list) != 2:
                print(f'Invalid line: {line}')
                continue
            color_map[int(line[0])] = temp_list[0], temp_list[1]


class BaseColor(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        self.color_set: Optional[tuple] = None

    def is_positive(self) -> bool:
        raise NotImplementedError

    def get_color(self):
        return self.color_set[0] if self.is_positive() else self.color_set[1]


T = TypeVar('T', int, float)


class BaseValue(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        self.value: Optional[T] = None
        self.format_list: Optional[list[str]] = None

    def is_positive(self) -> bool:
        return self.value >= 0

    def __str__(self) -> str:
        if not self.format_list:
            return f'{self.value}'
        else:
            if isinstance(self.value, int):
                mark_order: list[str] = [r'\+', r'\,']
            elif isinstance(self.value, float):
                mark_order: list[str] = [r'\+', r'\,', r'\.\d', r'\.\d%']
            else:
                raise TypeError
            valid_list: list[str] = []
            format_str: str = '{:'
            for i in mark_order:
                for j in self.format_list:
                    result = re.search(i, j)
                    if result and result.group(0) == j:
                        format_str += j
                        valid_list.append(j)
            if set(valid_list) != set(self.format_list):
                print(f'Invalid format: {self.format_list}')
                raise ValueError(f'Invalid format: {self.format_list}')
            if isinstance(self.value, int):
                format_str += 'd}'
            elif isinstance(self.value, float):
                if any(re.search(r'\.\d%', i) for i in self.format_list):
                    format_str += '}'
                else:
                    format_str += 'f}'
            try:
                return format_str.format(self.value)
            except ValueError as e:
                print(e)
                print(f'Invalid format: {self.format_list}')
                return f'{self.value}'


class IntValue(BaseValue):
    def __init__(self, value, *args: Optional[str], **kwargs):
        super().__init__()
        self.value: int = int(value)
        self.format_list: list[str] = list(args)


class FloatValue(BaseValue):
    def __init__(self, value, *args: Optional[str], **kwargs):
        super().__init__()
        self.value: float = float(value)
        self.format_list: list[str] = list(args)


def get_ColorValue_class(index: int, value_type: str) -> type:
    color_set = color_map[index]
    if value_type == 'int':
        class ColorValue(IntValue, BaseColor):
            def __init__(self, value, *args: Optional[str], **kwargs):
                super().__init__(value, *args, **kwargs)
                self.color_set: tuple = color_set
    elif value_type == 'float':
        class ColorValue(FloatValue, BaseColor):
            def __init__(self, value, *args: Optional[str], **kwargs):
                super().__init__(value, *args, **kwargs)
                self.color_set: tuple = color_set
    else:
        raise ValueError(f'Invalid value type: {value_type}')
    return ColorValue


class Time:
    def __init__(self, value: datetime, time_format: str, *args, **kwargs):
        self.value: datetime = value
        try:
            self.time_format: str = self.value.strftime(time_format)
        except ValueError:
            raise ValueError(f'Invalid time format: {time_format}')

    def __str__(self) -> str:
        return self.time_format


func = get_ColorValue_class(1, 'float')
print(func(1232.66575, '+', ',', '.5%'))
# print(ColorValue(123234, ('red', 'green'), '+', ','))
