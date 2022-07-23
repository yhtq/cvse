import re
import requests
import time
import json

plan = ['策']
lyrics = ['作 词', '作词', '词', '词作', 'lyric']
song_writer = ['作 曲', 'music', '作曲', '(?<![原前续制])作(?![品词/s])', '(?<![原编尾终序歌色])曲(?!绘)']
arrangement = ['编 曲', '编曲', '编', 'arrangement']
mix = ['混 音', '混音', '混', 'mix']
turing = ['调 教', '调 校', '调 音', '调教', '调音', '调校', '调', 'Tuning']
painting = ['曲 绘', '插画', '曲绘', '绘', 'Illust']
PV = ['动画', '(?<!dee)PV', '视频', '视', '影', '映像', 'motion']
instrument = ['二胡', '笛子', '琵琶', '吉他', 'Bass', '古筝']
vsqx = ['vsqx', '工程', 'svp', 'ust', '扒谱']
assistance = ['协力', '感谢', '特别感谢', 'special thank', 'special thanks', 'thanks', '鸣谢']
cover = ['封面']
total = plan + lyrics + song_writer + arrangement + mix + turing + painting + PV + assistance + cover


def collect(text: str, key_word_list: list):
    _str = ''
    for i in key_word_list:
        try:
            _str = re.search(r'' + i + '(?:.*?)([-|＆:： ]|by)+([^。\u0020\u3000；;\t\n\r\f\x0B【】|]+)', text, re.I).group(
                2)
            break
        except:
            continue
    return _str


def collect_staff(text):
    # {'策': p, '曲': sw, '编': a, '词': l, '调': t, '混': m, '绘': pa, '视': pv}
    flag = 0
    for i in total:
        for g in total:
            if re.search(r'(?<={})[/,，&]+(?={})'.format(g, i), text):
                flag = 1
                break
        if not flag:
            text = re.sub(r'[/,，&]+(?={})'.format(i), '\n', text)
    (p, sw, a, l, t, m, pa, pv, instr, _vsqx, assis, _cover) = (collect(text, plan), collect(text, song_writer), collect(text, arrangement),
                                                 collect(text, lyrics), collect(text, turing), collect(text, mix), collect(text, painting),
                                                 collect(text, PV), collect(text, instrument), collect(text, vsqx), collect(text, assistance), collect(text, cover))

    return {'策': p, '曲': sw, '编': a, '词': l, '调': t, '混': m, '绘': pa, '视': pv, '奏': instr, '协': assis, '封': _cover, '工程': _vsqx}


def request(url):
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
    except requests.RequestException as e:
        time.sleep(1)
        print('尝试重新连接')
        return request(url)
    return res


def degeneracy(dictionary):
    new_dict = {}
    done = ['']
    for key, value in dictionary.items():
        if value not in done:
            keys = [key]
            for key2, value2 in dictionary.items():
                if value == value2 and not key2 in keys:
                    keys.append(key2)
            done.append(value)
            new_dict['/'.join(keys)] = value
    return new_dict


def string(dictionary):
    _string = []
    for key, value in dictionary.items():
        _string.append(f'{key}:{value}')
    _string = '  '.join(_string)
    return _string


class Staff:
    # 简并前字典格式为{'策': p, '曲': sw, '编': a, '词': l, '调': t, '混': m, '绘': pa, '视': pv}
    def __init__(self, text: str, flag: int):
        # flag=1表示直接传入文本，否则表示传入aid(纯数）
        if flag:
            self.text = text
        elif text.isdigit():
            res2 = request('https://api.bilibili.com/x/web-interface/view?aid=' + str(text))
            res2 = json.loads(res2.text)
            self.text = res2['data']['desc']
        self.staff_dict_non_degeneracy = collect_staff(self.text)
        self.staff_dict_degeneracy = degeneracy(self.staff_dict_non_degeneracy)
        self.staff_dict_degeneracy_str = string(self.staff_dict_degeneracy)
        self.staff_dict_non_degeneracy_str = string(self.staff_dict_non_degeneracy)

    def translate(self, translate_dict):
        # 改变键,translate_dict格式为{'策':...,'曲':...}
        new_dict = {}
        for key, value in translate_dict.items():
            if key in self.staff_dict_non_degeneracy:
                if not value in new_dict:
                    new_dict[value] = self.staff_dict_non_degeneracy[key]
                else:
                    new_dict[value] += ',' + self.staff_dict_non_degeneracy[key]
        return new_dict

    def translate_degeneracy(self, translate_dict):
        # 改变键,translate_dict格式为{'策':...,'曲':...}
        new_dict = self.translate(translate_dict)
        return degeneracy(new_dict)
