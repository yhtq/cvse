from __future__ import annotations

import copy
import csv
import time
import datetime
from datetime import datetime

import openpyxl as op
from collections.abc import Callable
from typing import Callable, ParamSpec, ParamSpecArgs, ParamSpecKwargs, Concatenate, TypeVar
import openpyxl.styles

header = ['名次', '上次', 'aid', '标题', 'mid', 'up主', '投稿时间', '时长', '分P数', '播放增量', '弹幕增量', '评论增量',
          '收藏增量', '硬币增量', '分享增量',
          '点赞增量', 'Pt', '修正A', '修正B', '修正C', '长期入榜及期数', '收录', "引擎", '原创', "主榜", 'Last Pt',
          'rate', 'staff', '新曲排名', '新曲', '未授权搬运', '已删稿', 'HOT']
xlsx_header = ['名次', '上次', 'aid', '标题', 'mid', 'up主', '投稿时间', '时长', '分P数', '播放增量', '弹幕增量',
               '评论增量', '收藏增量', '硬币增量',
               '分享增量',
               '点赞增量', 'Pt', '修正A', '修正B', '修正C', 'Last Pt', 'rate', '长期入榜及期数', '新曲排名', 'staff',
               '原创', '引擎']
history_header = ['名次', '上次', 'aid', '标题', 'up主', '投稿时间', '时长', '分P数', '播放增量', '弹幕增量',
                  '评论增量', '收藏增量', '硬币增量',
                  '分享增量',
                  '点赞增量', 'Pt', '修正A', '修正B', '修正C', 'Last Pt', 'rate', 'staff']
xlsx_header_index = {i + 1: header[i] for i in range(len(header))}


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        print(f'cost:{time.time() - start_time}')

    return wrapper()


P = ParamSpec('P')
T = TypeVar("T")


def permission_access_decorator(func: Callable[[Concatenate[str, P]], T]) -> Callable[[Concatenate[str, P]], T]:
    def wrapper(file: str, *args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(file, *args, **kwargs)
        except PermissionError:
            print(f"{file}被占用，请关闭文件后按任意键重试")
            input()
            return wrapper(file, *args, **kwargs)

    return wrapper


class Data:
    pub_time_datetime: datetime
    main_flag = 0  # 主榜/副榜 flag
    header_word_to_digit = {'名次': 0, '上次': 1, 'aid': 2, '标题': 3, 'mid': 4, 'up主': 5,
                            '投稿时间': 6, '时长': 7, '分P数': 8, '播放增量': 9, '弹幕增量': 10,
                            '评论增量': 11, '收藏增量': 12, '硬币增量': 13, '分享增量': 14, '点赞增量': 15,
                            'Pt': 16, '修正A': 17, '修正B': 18, '修正C': 19, 'Last Pt': 20, 'rate': 21}
    header_digit_to_word = {value: key for key, value in header_word_to_digit.items()}
    int_data = ['aid', 'mid', '时长', '分P数', '播放增量', '弹幕增量', '评论增量', '收藏增量', '硬币增量', '分享增量',
                '点赞增量', '长期入榜及期数', '收录', '新曲排名', '已删稿']
    float_data = ['Pt', '修正A', '修正B', '修正C']
    ignore = ['HOT', '新曲排名', '长期入榜及期数', "主榜"]  # 这些列不读入数据

    @staticmethod
    def write_to_xlsx_wrapper(file_name: str, header: list['str'] | str = None):
        if header is None:
            header = xlsx_header
        if header == 'history':
            header = history_header
        wb = op.Workbook()
        ws = wb.active
        for idx, key in enumerate(header):
            ws.cell(row=1, column=idx + 1).value = key
        line = 2

        def write_to_xlsx(self: Data):
            nonlocal line
            nonlocal ws
            font, pattern, border = self.xlsx_cell_style()
            for idx, key in enumerate(header):
                try:
                    if key in ['修正A', '修正B', '修正C']:
                        ws.cell(row=line, column=idx + 1).value = round(float(self[key]), 3)
                        ws.cell(row=line, column=idx + 1).number_format = '0.000'
                    elif key == 'rate':
                        ws.cell(row=line, column=idx + 1).value = round(float(self[key]), 6)
                        ws.cell(row=line, column=idx + 1).number_format = '0.000%'
                    elif key in ['播放增量', '弹幕增量', '评论增量', '收藏增量', '硬币增量', '分享增量', '点赞增量',
                                 'Pt', 'Last Pt']:
                        ws.cell(row=line, column=idx + 1).value = int(float(self[key]))
                        ws.cell(row=line, column=idx + 1).number_format = '#,##0'
                    elif key == '投稿时间':
                        ws.cell(row=line, column=idx + 1).value = self[key]
                        ws.cell(row=line, column=idx + 1).number_format = 'yyyy/mm/dd hh:mm'
                    elif key == '新曲排名':
                        if int(float(self[key])) == 0:
                            ws.cell(row=line, column=idx + 1).value = None
                        else:
                            ws.cell(row=line, column=idx + 1).value = int(float(self[key]))
                            ws.cell(row=line, column=idx + 1).number_format = '000'
                    elif str(self[key]).isdigit():
                        ws.cell(row=line, column=idx + 1).value = int(self[key])
                    else:
                        ws.cell(row=line, column=idx + 1).value = self[key]
                except ValueError:
                    ws.cell(row=line, column=idx + 1).value = self[key]
                ws.cell(row=line, column=idx + 1).font = font
                ws.cell(row=line, column=idx + 1).fill = pattern
                ws.cell(row=line, column=idx + 1).border = border
            line += 1
            return

        def save_close():
            @permission_access_decorator
            def _save_close(file: str):
                nonlocal wb
                wb.save(file)
                wb.close()

            _save_close(file_name)

        return write_to_xlsx, save_close

    @staticmethod
    def write_to_csv_wrapper(file_name: str, _header: list = header) \
            -> (Callable[[Data, bool, bool], None], Callable[[None], None]):
        #  一次性写入，覆盖原有数据

        @permission_access_decorator
        def __open(file: str):
            f = open(file_name, 'w+', encoding='utf-8-sig', newline='')
            writer = csv.DictWriter(f, fieldnames=_header)
            writer.writeheader()
            return f, writer

        f, writer = __open(file_name)

        def write_to_csv(self: Data, with_seconds: bool = False, with_format: bool = False) -> None:
            dict_to_write = {key: value for key, value in self.dict_.items() if key in _header}
            if with_seconds:
                dict_to_write['投稿时间'] = self.pub_time_datetime.strftime('%Y/%m/%d %H:%M:%S')
            else:
                dict_to_write['投稿时间'] = self.pub_time_datetime.strftime('%Y/%m/%d %H:%M')
            if with_format:
                for key in _header:
                    try:
                        if key in ['修正A', '修正B', '修正C']:
                            dict_to_write[key] = f'{float(self[key]):.3f}'
                        elif key == 'rate':
                            dict_to_write[key] = f'{float(self[key]) * 100:.3f}%'
                        elif key in ['播放增量', '弹幕增量', '评论增量', '收藏增量', '硬币增量', '分享增量', '点赞增量',
                                     'Pt', 'Last Pt']:
                            dict_to_write[key] = f'{int(float(self[key])):,}'
                        elif key == '新曲排名':
                            if int(float(self[key])) == 0:
                                dict_to_write[key] = ''
                            else:
                                dict_to_write[key] = f'{int(float(self[key])):03}'
                        elif str(self[key]).isdigit():
                            dict_to_write[key] = f'{int(self[key])}'
                        else:
                            dict_to_write[key] = f'{self[key]}'
                    except ValueError:
                        dict_to_write[key] = f'{self[key]}'
            writer.writerow(dict_to_write)

        def save_close() -> None:
            f.close()

        return write_to_csv, save_close

    def __init__(self, data: dict | list | tuple, data_type: str, file_header: list = None):
        # data_type必须为"xlsx"或“csv", data 是tuple, list, dict其中之一，前两者要求提供列索引(list)，
        if file_header is None:
            self.file_header = [0]
        else:
            self.file_header = file_header  # xlsx第i列列索引，从1开始
        if data_type == 'csv':
            if isinstance(data, dict):
                self.dict_ = data
            elif isinstance(data, (list, tuple)):
                if self.file_header == [0] or len(data) < len(self.file_header):
                    print("列索引错误")
                    input()
                    raise ValueError
                else:
                    self.dict_ = {self.file_header[i]: data[i] for i in range(len(self.file_header))}
            else:
                print("类型错误")
                input()
                raise TypeError
        elif data_type == 'xlsx':
            if self.file_header == [0] or len(data) > len(self.file_header) - 1:
                print("列索引不足")
                input()
                raise RuntimeError
            dict_ = {}
            for idx, k in enumerate(data):
                dict_[self.file_header[idx + 1]] = k.value
                try:
                    if not k.fill is None:
                        if k.fill.start_color.rgb[2:] == 'FFFF00':
                            dict_['收录'] = 0
                        if k.fill.start_color.rgb[2:] in ['C00000', 'FF0000', '92D050']:
                            dict_['原创'] = '原创'
                            dict_['收录'] = 1
                        if k.fill.start_color.rgb[2:] == 'FFC000':
                            dict_['未授权搬运'] = '未授权搬运'
                            dict_['收录'] = 1
                except AttributeError:
                    pass
                try:
                    if not k.border.bottom is None:
                        if k.border.bottom.style == 'medium':
                            if not Data.main_flag:
                                dict_['主榜'] = '主榜截止'  # 主榜到此截止
                                Data.main_flag = 1
                            else:
                                dict_['主榜'] = '副榜截止'  # 副榜截止
                                Data.main_flag = 0
                except AttributeError:
                    pass
            self.dict_ = dict_
            if 'aid' not in self.dict_.keys():
                print('没有找到aid')
                print(data)
                input()
                raise ValueError
        else:
            print('文件格式错误')
            input()
            raise ValueError
        for i in Data.ignore:
            if i in self.dict_.keys():
                self.dict_[i] = ''
        if str(self.dict_.get('原创')) == '1':
            self.dict_['原创'] = '原创'
        if not (isinstance(self['aid'], int) or self['aid'].isdigit()):
            self.valid = False
        else:
            self.valid = True
        if '收录' in self.dict_.keys() and isinstance(self.dict_['收录'], str) and self.dict_['收录'].isdigit():
            self.dict_['收录'] = int(self.dict_['收录'])
        if '排名' in self.dict_.keys():
            self.dict_['名次'] = self.dict_['排名']
        if '投稿时间' in self.dict_.keys() and isinstance(self.dict_['投稿时间'], str):
            try:
                self.pub_time_time_struct = time.strptime(self.dict_['投稿时间'], '%Y/%m/%d %H:%M:%S')
            except ValueError:
                try:
                    self.pub_time_time_struct = time.strptime(self.dict_['投稿时间'], '%Y/%m/%d %H:%M')
                except ValueError:
                    try:
                        self.pub_time_time_struct = time.strptime(self.dict_['投稿时间'], '%Y-%m-%d %H:%M')
                    except ValueError:
                        self.pub_time_time_struct = time.strptime(self.dict_['投稿时间'], '%Y-%m-%d %H:%M:%S')
        else:
            self.pub_time_time_struct = time.strptime('1970/01/01 00:00:10', '%Y/%m/%d %H:%M:%S')
        if '投稿时间' in self.dict_.keys():
            if isinstance(self.dict_['投稿时间'], datetime):
                self.pub_time_datetime = self['投稿时间']
                self['投稿时间'] = self.dict_['投稿时间'].strftime('%Y-%m-%d %H:%M')
                self.pub_time_time_struct = time.strptime(self.dict_['投稿时间'], '%Y-%m-%d %H:%M')
            else:
                self.pub_time_datetime = datetime.fromtimestamp(time.mktime(self.pub_time_time_struct))
                self.dict_['投稿时间'] = time.strftime('%Y/%m/%d %H:%M', self.pub_time_time_struct)
        for key in header + self.file_header:
            if key not in self.dict_.keys() or self.dict_[key] is None:
                self.dict_[key] = ''
        if 0 in self.dict_.keys():
            del self.dict_[0]
        _staff = 1
        del_list = []
        for key in self.dict_.keys():
            if isinstance(key, str) and key.lower() == 'staff':
                _staff = self.dict_[key]
                del_list.append(key)
        for key in del_list:
            del self.dict_[key]
        self.dict_['staff'] = _staff
        for key in Data.int_data:
            if key in self.dict_.keys() and isinstance(self.dict_[key], (str, float)) and self.dict_[key] not in ['',
                                                                                                                  '-',
                                                                                                                  '--']:
                self.dict_[key] = int(round(float(self.dict_[key]), 0))
        for key in Data.float_data:
            if key in self.dict_.keys() and isinstance(self.dict_[key], (str, float)) and self.dict_[key] not in ['',
                                                                                                                  '-',
                                                                                                                  '--']:
                self.dict_[key] = float(self.dict_[key])
        if '引擎' in self.dict_.keys() and isinstance(self.dict_['引擎'], str):
            if self.dict_['引擎'].lower() == 'aisinger':
                self.dict_['引擎'] = 'AISingers'
            elif self.dict_['引擎'].lower() == 'muta':
                self.dict_['引擎'] = 'MUTA'
            elif self.dict_['引擎'].lower() == 'dv':
                self.dict_['引擎'] = 'DeepVocal'
            elif self.dict_['引擎'].lower() == 'sk':
                self.dict_['引擎'] = 'Sharpkey'
            elif self.dict_['引擎'] == '袅袅':
                self.dict_['引擎'] = '袅袅虚拟歌手'
            elif self.dict_['引擎'].lower() == 'xstudio' or self.dict_['引擎'].lower() == 'x studio':
                self.dict_['引擎'] = 'X Studio'

    def write_to_csv(self,
                     file_name: str,
                     head: list[str],
                     with_seconds: bool = False) -> None:
        #  续写，分条写入
        @permission_access_decorator
        def _write(file_name: str):
            nonlocal self
            dict_to_write = {key: value for key, value in self.dict_.items() if key in head}
            if with_seconds:
                dict_to_write['投稿时间'] = self.pub_time_datetime.strftime('%Y/%m/%d %H:%M:%S')
            else:
                dict_to_write['投稿时间'] = self.pub_time_datetime.strftime('%Y/%m/%d %H:%M')
            with open(file_name, 'a+', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=head)
                writer.writerow(dict_to_write)

        _write(file_name)

    def is_new(self) -> bool:
        if self['新曲'] in ['新曲榜', '新曲']:
            return True
        if '上次' in self.dict_.keys():
            return self['上次'] == 'NEW'
        return False

    def xlsx_cell_style(self) -> (op.styles.Font, op.styles.PatternFill, op.styles.Border):
        font = op.styles.Font(name='等线', size=11)
        pattern = op.styles.PatternFill()
        border = op.styles.Border()
        if self['长期入榜及期数'] != '':
            pattern = op.styles.PatternFill(fill_type='solid', fgColor='FFC000', start_color='FFC000',
                                            end_color='FFC000')
            font.bold = True
        if self['主榜'] in ['主榜截止', '副榜截止']:
            border.bottom = op.styles.Side(style='medium', color='000000')
        if self['HOT'] == 'HOT':
            pattern = op.styles.PatternFill(fill_type='solid', fgColor='7030A0', start_color='7030A0',
                                            end_color='7030A0')
            font.color = op.styles.Color(rgb='FFFFFF')
            font.bold = True
        if not self.is_new():
            return font, pattern, border
        if self['原创'] == '原创' and self.is_new():
            pattern = op.styles.PatternFill(fill_type='solid', fgColor='C00000', start_color='C00000',
                                            end_color='C00000')
            font.color = op.styles.Color(rgb='FFFFFF')
            font.bold = True
        if self['原创'] == '榜外原创':
            pattern = op.styles.PatternFill(fill_type='solid', fgColor='92D050', start_color='92D050',
                                            end_color='92D050')
            font.bold = True
        if self['未授权搬运'] == '未授权搬运':
            pattern = op.styles.PatternFill(fill_type='solid', fgColor='FFC000', start_color='FFC000',
                                            end_color='FFC000')
            font.bold = True
        if self['收录'] == 0:
            pattern = op.styles.PatternFill(fill_type='solid', fgColor='FFFF00', start_color='FFFF00',
                                            end_color='FFFF00')
        return font, pattern, border

    def add_info(self, other, key=None):  # 添加信息，只会添加为没有或为空值的键值，不改变已有的键值
        if not self.is_same_song(other):
            print('aid不一致,不能合并')
            input()
            raise ValueError
        if key is None:
            for _key in other.dict_.keys():
                if _key not in self.dict_.keys():
                    self[_key] = other[_key]
                else:
                    if self[_key] == '':
                        self[_key] = other[_key]
        else:
            if key not in self.dict_.keys():
                self[key] = other[key]
            else:
                if self[key] == '' and other[key] != '':
                    self[key] = other[key]
        return

    def __getitem__(self, item):
        if isinstance(item, str) and item.lower() == 'staff':
            return self.dict_['staff']
        if item in ['名次', '排名']:
            return self.dict_['名次']
        if isinstance(item, str) and item.lower() == 'lastpt':
            return self.dict_['Last Pt']
        elif item in self.dict_.keys():
            return self.dict_[item]
        elif item in Data.header_digit_to_word.keys():
            return self.dict_[Data.header_digit_to_word[item]]
        else:
            print("未知的key:", item)
            input()
            raise ValueError

    def __setitem__(self, key, value):
        if isinstance(key, str) and key.lower() == 'staff':
            self.dict_['staff'] = value
        if key in ['名次', '排名']:
            self.dict_['名次'] = value
        if isinstance(key, str) and key.lower() == 'lastpt':
            self.dict_['Last Pt'] = value
        elif key in self.dict_.keys():
            self.dict_[key] = value
        elif key in Data.header_digit_to_word.keys():
            self.dict_[Data.header_digit_to_word[key]] = value
        else:
            print("未知的key", key)
            input()
            raise ValueError

    def __len__(self):
        return len(self.dict_.keys())

    def __lt__(self, other):
        if (self['HOT'] != 'HOT' and other['HOT'] != 'HOT') or (self['HOT'] == 'HOT' and other['HOT'] == 'HOT'):
            if float(self['Pt']) != float(other['Pt']):
                return float(self['Pt']) < float(other['Pt'])
            elif '投稿时间' in self.dict_.keys() and '投稿时间' in other.dict_.keys():
                return self.pub_time_datetime < other.pub_time_datetime
            else:
                return True
        else:
            if self['HOT'] == 'HOT':
                return False
            else:
                return True

    def is_same_song(self, other):
        return int(self['aid']) == int(other['aid'])


Data_type = TypeVar('Data_type')


@permission_access_decorator
def read(file_path: str, class_type: Data_type, max_rank: int = -1) -> list[Data_type]:
    data_list = []
    if file_path.split('.')[-1] == 'csv':
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for g, i in enumerate(reader):
                    progress = int(g * 100 / reader.line_num)
                    if progress % 10 == 0:
                        print(f'{progress}%')
                    new_data = class_type(i, 'csv')
                    if new_data.valid:
                        data_list.append(new_data)
                        if (str(new_data['名次']) == str(max_rank)) and (max_rank != -1):
                            break
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for g, i in enumerate(reader):
                    progress = int(g * 100 / reader.line_num)
                    if progress % 10 == 0:
                        print(f'{progress}%')
                    new_data = class_type(i, 'csv')
                    if new_data.valid:  # 避免空行
                        data_list.append(new_data)
                        if (str(new_data['名次']) == str(max_rank)) and (max_rank != -1):
                            break
    elif file_path.split('.')[-1] == 'xlsx':
        wb = op.load_workbook(file_path, read_only=True)
        sheet = wb.active
        xlsx_order = [0]
        for g in sheet[1]:
            xlsx_order.append(g.value)
        last_process = 0
        row_count = sheet.max_row
        for g, row in enumerate(sheet.rows):
            if g == 0:
                continue
            progress = int((g - 1) * 100 / row_count)
            if progress % 10 == 0 and progress != last_process:
                print(str(progress) + '%')
                last_process = progress
            new_data = class_type(row, 'xlsx', xlsx_order)
            if new_data.valid:
                data_list.append(new_data)
            if (str(new_data['名次']) == str(max_rank)) and (max_rank != -1):
                break
    else:
        print("文件名格式错误")
        input()
        raise RuntimeError
    print("读取完成")
    return data_list
