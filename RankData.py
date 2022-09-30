import datetime
import json
import os
from abc import ABC
from functools import partial

import pptx
from PIL import Image
from typing import List, Union, Tuple, Callable, Optional

import dateutil.relativedelta
import SongData
import CVSE_Data
import downloader
from downloader import download_cover
from ppt.VariablesClass import BaseValue


@CVSE_Data.permission_access_decorator
def remove(path: str):
    os.remove(path)


@CVSE_Data.permission_access_decorator
def load_record(file: str) -> Callable[[Callable], Callable]:
    record = {}
    if not os.path.exists(os.path.split(file)[0]):
        os.makedirs(os.path.split(file)[0])
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            record = json.load(f)

    def _load_record(func: Callable) -> Callable:
        def _func(*args, **kwargs):
            nonlocal record
            node = record
            for arg in args[0:-1]:
                if str(arg) not in node:
                    node[str(arg)] = {}
                node = node[str(arg)]
            if str(args[-1]) in node:
                return node[str(args[-1])]
            node[str(args[-1])] = func(*args, **kwargs)
            with open(file, "w", encoding="utf-8") as f:
                json.dump(record, f)
            return node[str(args[-1])]

        return _func

    return _load_record


def calculate_time(_rank: int, _index: int) -> Tuple[datetime.datetime, datetime.datetime]:
    if _rank == 0:  # 国产榜
        basic_time_start = datetime.datetime.strptime("2021/04/28 3:00", "%Y/%m/%d %H:%M")
        basic_time_end = datetime.datetime.strptime("2021/05/28 3:00", "%Y/%m/%d %H:%M")
        time_start = basic_time_start + dateutil.relativedelta.relativedelta(months=_index - 48)
        time_end = basic_time_end + dateutil.relativedelta.relativedelta(months=_index - 48)
        return time_start, time_end
    if _rank == 1:  # SV刊
        basic_time_start = datetime.datetime.strptime("2021/11/26 3:00", "%Y/%m/%d %H:%M")
        basic_time_end = datetime.datetime.strptime("2021/12/03 3:00", "%Y/%m/%d %H:%M")
        time_start = basic_time_start + datetime.timedelta(weeks=_index - 132)
        time_end = basic_time_end + datetime.timedelta(weeks=_index - 132)
        return time_start, time_end
    print("Error: Rank is not 0 or 1")
    # input("Press Enter to exit")
    raise ValueError


def calculate_index(_rank: int, time_start: datetime.datetime) -> int:
    if _rank == 0:
        temp = dateutil.relativedelta.relativedelta(dt1=time_start,
                                                    dt2=datetime.datetime.strptime("2021/04/28 3:00", "%Y/%m/%d %H:%M"))
        return temp.years * 12 + temp.months + 48
    if _rank == 1:
        temp = time_start - datetime.datetime.strptime("2021/11/26 3:00", "%Y/%m/%d %H:%M")
        return temp.days // 7 + 132
    print("Error: Rank is not 0 or 1")
    # input("Press Enter to exit")
    return -1


def calculate_week(time: datetime.datetime) -> int:
    # 计算是当月第几周
    start_day_of_month = datetime.datetime(time.year, time.month, 1)
    return (time - start_day_of_month).days // 7 + 1


def calculate_history(rank: int, index: int) -> int:
    # 返回去年当期期数。若小于零则为0
    start_time, _ = calculate_time(rank, index)
    his_index: int = calculate_index(rank, start_time - dateutil.relativedelta.relativedelta(years=1))
    if rank == 1:
        his_index += 1
        # SV刊的历史回顾是指当前期收录起始时间减去一年所在的下一期
    return his_index if his_index > 0 else 0


class BaseRankData(ABC):
    def __init__(self):
        self.dict_for_replace = {}

    def __getitem__(self, item):
        if item in self.dict_for_replace:
            return self.dict_for_replace[item]
        else:
            print(f'{self.__class__.__name__}对象中没有{item}这个属性')
            print('按任意键继续')
            input()
            raise KeyError

    def __contains__(self, item):
        return item in self.dict_for_replace


Slide = pptx.slide.Slide
Shapes = pptx.shapes.shapetree.SlideShapes
Run = pptx.text.text._Run
Value = Union[BaseValue, CVSE_Data.Data_value_type]
Class = Union[CVSE_Data.Data, BaseRankData, None]
ValidMember = Union[BaseValue,
                    str,
                    CVSE_Data.Data,
                    CVSE_Data.Data_value_type,
                    Image.Image,
                    List[CVSE_Data.Data_value_type],
                    None]
Member = Optional[ValidMember]
TableType = List[Value]
RootType = Union[dict[str, Class], Class]


class RankData(BaseRankData):
    data_list: list[str] = ['播放', '弹幕', '评论', '收藏', '硬币', '分享', '点赞']
    engine_list: list[str] = ['袅袅虚拟歌手', 'MUTA', 'Sharpkey', 'DeepVocal', 'AISingers', 'X Studio', 'VocalSharp',
                              'Vogen', '其他/跨引擎']

    # 应正佬要求按发布时间排序引擎

    def __init__(self, data: list[CVSE_Data.Data], index: int, rank: int):
        super().__init__()
        data.sort(reverse=True)
        self.index: int = index
        self.rank: int = rank
        self.Data_list = data
        self.time_start, self.time_end = calculate_time(rank, index)
        for i in self.data_list:
            if i + '增量' not in self.Data_list[0].required_keys:
                print(f'第{index}期数据未保证包含{i}增量')
                print('按任意键继续')
                input()
                raise KeyError
        self.count: dict[str, int] = {i: 0 for i in RankData.data_list + ['新曲']}  # 只需计数
        for i in RankData.engine_list + ['原创']:
            self.count[i] = 0
        self.aid_list: dict[str, list[int]] = {i: [] for i in RankData.engine_list + ['原创']}  # 需减去上期
        # 注意Data类中收录值若无信息默认为’‘，需要特殊赋值，Pres_data类中收录值可能为0,1
        if any(i['收录'] == '' for i in data):
            print(f'在计算第{index}期榜单信息时不应该有收录状态待定的数据')
            input('按任意键退出')
            raise ValueError
        for _i in filter(lambda x: x['收录'] == 1, data):
            for j in RankData.data_list:
                self.count[j] += _i[j + '增量']  # type: ignore
        for _i in filter(lambda x: x['收录'] == 1 and self.is_pres_new(x), self.Data_list):
            # 这些数据只计算新曲
            self.count['新曲'] += 1
            if _i['原创'] in ['原创', '榜外原创']:
                self.aid_list['原创'] += [_i['aid']]  # type: ignore
                self.count['原创'] += 1
            if _i['引擎'] in RankData.engine_list:
                self.count[_i['引擎']] += 1  # type: ignore
                self.aid_list[_i['引擎']].append(_i['aid'])  # type: ignore
        # try:
        # print([i['主榜'] for i in self.Data_list])
        self.dict_for_replace: dict[str, Member] = {
            'index': self.index,
            'start_time': self.time_start,
            'first': max(filter(lambda x: x['收录'] == 1 and str(x['名次']).lower() != 'hot', data)),
            'week': calculate_week(self.time_end),
            'end_time': self.time_end,
            'new_total': self.count['新曲'],
            'ori_total': self.count['原创'],
            'view': self.count['播放'],
            'danmaku': self.count['弹幕'],
            'reply': self.count['评论'],
            'favorite': self.count['收藏'],
            'coin': self.count['硬币'],
            'share': self.count['分享'],
            'like': self.count['点赞'],
            '袅袅虚拟歌手': self.count['袅袅虚拟歌手'],
            'MUTA': self.count['MUTA'],
            'Sharpkey': self.count['Sharpkey'],
            'DeepVocal': self.count['DeepVocal'],
            'AISingers': self.count['AISingers'],
            'X Studio': self.count['X Studio'],
            'VocalSharp': self.count['VocalSharp'],
            'Vogen': self.count['Vogen'],
            '其他/跨引擎': self.count['其他/跨引擎'],
            'startpt': None,
            'side_startpt': None,
            'top1_view': self.Data_list[0],
            'top1_view_value': self.Data_list[0]['播放增量']
        }
        self.dict_to_get: dict[str, Union[Member, Callable[[], Member]]] = {  # 信息待定
            'aid': partial(get_history_av, rank=self.rank, index=self.index),
            'bvid': partial(get_history_bv, rank=self.rank, index=self.index),
            'cover': partial(get_history_cover, rank=self.rank, index=self.index),
        }
        for i in filter(lambda x: x['收录'] == 1, data):  # type: ignore
            if i['主榜'] == '主榜截止':  # type: ignore
                self.dict_for_replace['startpt'] = i['Pt']  # type: ignore
            if i['主榜'] == '副榜截止':  # type: ignore
                self.dict_for_replace['side_startpt'] = i['Pt']  # type: ignore
            if int(i['播放增量']) > int(self.dict_for_replace['top1_view']['播放增量']):  # type: ignore
                self.dict_for_replace['top1_view'] = i  # 注意这里是歌曲对象不是播放量
                self.dict_for_replace['top1_view_value'] = i['播放增量']  # type: ignore
        if self.dict_for_replace['startpt'] is None:
            print(f'第{index}期榜单信息中没有主榜截止数据,请检查')
            input('按任意键继续')
            raise ValueError
        if self.dict_for_replace['side_startpt'] is None:
            print(f'第{index}期榜单信息中没有副榜截止数据,请检查')
            input('按任意键继续')
            raise ValueError
        # except IndexError as e:
        #    print(e)
        #    print(f'读取第{index}期榜单信息时出现错误')
        #    input('按任意键退出')
        # print(self.dict_for_replace)

    def is_pres_new(self, song: CVSE_Data.Data) -> bool:
        # 是否当期新曲
        if '投稿时间' in song.dict_:
            return self.time_start <= song.pub_time_datetime < self.time_end
        else:
            return False

    def __getitem__(self, item):
        if item in self.dict_to_get:
            if isinstance(self.dict_to_get[item], Callable):
                self.dict_to_get[item] = self.dict_to_get[item]()
            return self.dict_to_get[item]
        else:
            return super().__getitem__(item)

    def __contains__(self, item):
        return item in self.dict_to_get or super().__contains__(item)


class RankDataDelta(BaseRankData):
    key_list = {
        'new_total',
        'ori_total',
        'view',
        'danmaku',
        'reply',
        'favorite',
        'coin',
        'share',
        'like',
        'startpt',
        'top1_view_value',
        'side_startpt'
    }

    def __init__(self, pres_data: RankData, prev_data: RankData):
        super().__init__()
        self.data_delta = {}
        for key in RankData.data_list + ['新曲', '原创'] + RankData.engine_list:
            self.data_delta[key] = pres_data.count[key] - prev_data.count[key]
        self.dict_for_replace: dict[str, Union[int, float]] = {i: pres_data[i] - prev_data[i]
                                                               for i in RankDataDelta.key_list}


class RankDataRate(RankDataDelta):
    def __init__(self, pres_data: RankData, prev_data: RankData):
        super().__init__(pres_data, prev_data)
        self.dict_for_replace: dict[str, float] = {i: float(self.dict_for_replace[i]) / float(prev_data[i])
                                                   for i in RankDataRate.key_list}


pres_dir = os.path.join(os.path.dirname(__file__))


@load_record(os.path.join(pres_dir, 'Record/history.json'))
def get_history_avbv(rank: int, index: int) -> Tuple[int, str]:
    his_av_bv = input(f"请输入第{index}期(历史回顾)排行榜的aid/bvid，包含前缀av/BV")
    his_av, his_bv = SongData.get_av_bv(his_av_bv)
    return his_av, his_bv


def get_history_av(rank: int, index: int) -> int:
    return get_history_avbv(rank, index)[0]


def get_history_bv(rank: int, index: int) -> str:
    return get_history_avbv(rank, index)[1]


def get_history_cover(rank: int, index: int) -> Image.Image:
    av: int = get_history_av(rank, index)
    return download_cover(av, 'history', 0, False)
