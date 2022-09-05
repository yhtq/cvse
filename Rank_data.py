import datetime
from typing import List

import dateutil.relativedelta

import CVSE_Data


def calculate_time(_rank: int, _index: int) -> (datetime.datetime, datetime.datetime):
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


def calculate_index(_rank: int, time_start: datetime.datetime) -> int:
    if _rank == 0:
        temp = dateutil.relativedelta.relativedelta(dt1=time_start,
                                                    dt2=datetime.datetime.strptime("2021/04/28 3:00", "%Y/%m/%d %H:%M"))
        return temp.years * 12 + temp.months + 48
    if _rank == 1:
        temp = time_start - datetime.datetime.strptime("2021/11/26 3:00", "%Y/%m/%d %H:%M")
        return temp.days // 7 + 132


def calculate_week(time: datetime.datetime) -> int:
    # 计算是当年第几周
    return time.isocalendar()[1]
class Rank_data:
    data_list: list[str] = ['播放', '弹幕', '评论', '收藏', '硬币', '分享', '点赞']
    engine_list: list[str] = ['袅袅虚拟歌手', 'MUTA', 'Sharpkey', 'DeepVocal', 'AISingers', 'X Studio', 'VocalSharp', 'Vogen', '跨引擎']

    # 应正佬要求按发布时间排序引擎

    def __init__(self, data: list[CVSE_Data.Data], index: int, rank: int):
        self.index: int = index
        self.rank: int = rank
        self.Data_list = data
        self.time_start, self.time_end = calculate_time(rank, index)
        self.count = {i: 0 for i in Rank_data.data_list + ['新曲']}  # 只需计数
        for i in Rank_data.engine_list + ['原创']:
            self.count[i] = 0
        self.aid_list = {i: [] for i in Rank_data.engine_list + ['原创']}  # 需减去上期
        # 注意Data类中收录值若无信息默认为’‘，需要特殊赋值，Pres_data类中收录值可能为0,1
        if any(i['收录'] == '' for i in data):
            print(f'在计算第{index}期榜单信息时不应该有收录状态待定的数据')
            input('按任意键退出')
            raise ValueError
        for i in filter(lambda x: x['收录'] == 1, data):
            for j in Rank_data.data_list:
                self.count[j] += i[j + '增量']
        for i in filter(lambda x: x['收录'] == 1 and self.is_pres_new(x), self.Data_list):
            # 这些数据只计算新曲
            self.count['新曲'] += 1
            if i['原创'] in ['原创', '榜外原创']:
                self.aid_list['原创'] += [i['aid']]
                self.count['原创'] += 1
            if i['引擎'] in Rank_data.engine_list:
                self.count[i['引擎']] += 1
                self.aid_list[i['引擎']].append(i['aid'])
        self.dict_for_replace: dict[str] = {
            'index': self.index,
            'start_time': self.time_start,
            'first': max(filter(lambda x: x['收录'] == 1, data)),
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
            '跨引擎': self.count['跨引擎'],
            'startpt': [i['Pt'] for i in self.Data_list if i['收录'] == 1 and i['主榜'] == '主榜截止'][0],
            'side_startpt': [i['Pt'] for i in self.Data_list if i['收录'] == 1 and i['主榜'] == '副榜截止'][0],
            'top1_view': max(filter(lambda x: x['收录'] == 1, data), key=lambda x: x['播放增量'])['播放增量'],
        }
        #print(self.dict_for_replace)

    def is_pres_new(self, song: CVSE_Data.Data) -> bool:
        # 是否当期新曲
        if '投稿时间' in song.dict_:
            return self.time_start <= song.pub_time_datetime < self.time_end
        else:
            return False

    def __getitem__(self, item):
        return self.dict_for_replace[item]


class Rank_data_delta:
    def __init__(self, pres_data: Rank_data, prev_data: Rank_data):
        self.data_delta = {}
        self.data_new = {}
        for key in Rank_data.data_list + ['新曲']:
            self.data_delta[key] = pres_data.count[key] - prev_data.count[key]
        for key in Rank_data.engine_list + ['原创']:
            pres_new_count = [1 for i in pres_data.aid_list[key] if i not in prev_data.aid_list[key]]
            self.data_delta[key] = sum(pres_new_count) - prev_data.count[key]
            self.data_new[key] = sum(pres_new_count)
        self.data_delta['其他/跨引擎'] = self.data_delta['跨引擎']
        self.data_new['其他/跨引擎'] = self.data_new['跨引擎']
