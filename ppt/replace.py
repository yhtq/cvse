# 替换ppt中的文本
import os
import re
from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Callable, Optional, TypeVar, Union
import VariablesClass
import pptx

file: str = 'ppt_test.pptx'
ppt = pptx.Presentation(file)
alias_dict: dict[str, str] = {}
with open('数据别名.txt', 'r', encoding='utf-8') as f:
    for line in f.readlines():
        line = line.strip()
        if not line:
            continue
        if line[0] == '#':
            continue
        line = line.split('#')[0]
        if line:
            line = [i.strip() for i in line.split('=')]
            if len(line) != 2:
                print(f'Invalid line: {line}')
                continue
            alias_dict[line[0]] = line[1]

T = TypeVar('T', int, float, str, datetime)


def data_lookup(name: str) -> T:
    return 123000


def type_split(name: str) -> tuple[str, Optional[type]]:
    # 返回类型名和类型类
    for valuetype in ['int', 'float']:
        if name == valuetype:
            return valuetype, VariablesClass.IntValue if valuetype == 'int' else VariablesClass.FloatValue
        else:
            result = re.search(r'color' + valuetype, name)
            if result:
                color_index: int = 0
                if result.group(0) != name:
                    result = re.search(r'color' + valuetype + r'_\$(\d+)', name)
                    if result and result.group(0) == name:
                        color_index = int(result.group(1))
                    else:
                        print(f'Invalid type: {name}')
                        input()
                        raise ValueError
                return valuetype, VariablesClass.get_ColorValue_class(color_index, valuetype)
    if valuetype == 'str':
        return valuetype, str
    if valuetype == 'time':
        return valuetype, VariablesClass.Time
    if valuetype in ['Table', 'pic']:
        return valuetype, None
    raise ValueError(f'{name}')


def format_func(arg: str) -> Union[VariablesClass.BaseValue, str]:
    # 格式化成功返回相应对象，否则返回原字符串
    if arg in alias_dict:
        name = alias_dict[arg.strip()]
    else:
        name = arg.strip()
    args_list: list[str] = name.split(' ')
    if len(args_list) < 2:
        print(f'Invalid format: {arg}')
        return '{' + arg + '}'
    try:
        value_type, value_class = type_split(args_list[0])
    except ValueError as e:
        print(f'Invalid type: {e} in {name}')
        return '{' + arg + '}'
    if value_class is not None:
        try:
            value: T = value_class(data_lookup(args_list[1]), *args_list[2:])
            return value
        except ValueError as e:
            print(e)
            print(f'Invalid data or args: {args_list[1:]}')
            return '{' + arg + '}'
    else:
        return '{' + arg + '}'


def replace_text(func: Callable[[re.Match], str]):
    for slide in ppt.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        run.text = re.sub("r\{123}", func, run.text)


print(format_func('int 123.456 ,').with_color())
# ppt.save('test.pptx')
