import re
import time
from typing import Tuple, Union

import requests
import json
import collect_staff


def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


def request(url):
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
    except requests.RequestException as e:
        time.sleep(1)
        print('尝试重新连接')
        return request(url)
    return res


vocal_list = ['洛天依', '乐正绫', '言和', '乐正龙牙', '墨清弦', '徵羽摩柯', '心华', '初音未来', '镜音铃', '镜音连',
              '巡音流歌', '诗岸', '苍穹', '海伊', '赤羽',
              '艾可', '牧心', '牧馨', 'Minus', '叁琏', '嫣汐', '袅袅', '楚楚', '悦成', '起氏双子', '初音ミク', '起礼',
              '起复', '东方栀子', '莲华', '幻晓伊',
              '江上曜', '飞梦', '闇音', '天碎瓷']
Translate = {'view': '播放', 'danmaku': '弹幕', 'reply': '评论', 'favorite': '收藏', 'coin': '硬币', 'share': '分享',
             'like': '点赞'}


def get_info(av_bv: Union[int, str], flag: int):
    # flag:0为bv,1为av(指输入)
    if flag == 1:
        res2 = request('https://api.bilibili.com/x/web-interface/view?aid=' + str(av_bv))
        res2 = json.loads(res2.text)
    elif flag == 0:
        res2 = request('https://api.bilibili.com/x/web-interface/view?bvid=' + str(av_bv))
        res2 = json.loads(res2.text)
    elif flag == 2:
        res = request(
            f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&page=1&keyword={str(av_bv)}")
        res = json.loads(res.text)
        res2 = request('https://api.bilibili.com/x/web-interface/view?aid=' + str(res['data']['result'][0]['aid']))
        res2 = json.loads(res2.text)
    else:
        print('flag error')
        input()
        raise ValueError
    return res2


def convert_av_bv(av_bv: Union[int, str], flag: int) -> Tuple[int, str]:
    # flag:0为bv,1为av（指输入），av_bv无前缀
    data = get_info(av_bv, flag)
    return int(data['data']['aid']), data['data']['bvid']


def get_av_bv(av_bv: str) -> Tuple[int, str]:
    # 含前缀的av_bv,返回av,bv,返回值无前缀
    if (_prefix := av_bv[:2].lower()) == 'av':
        return convert_av_bv(av_bv[2:], 1)
    elif _prefix == 'bv':
        return convert_av_bv(av_bv[2:], 0)
    else:
        print(f'{av_bv}带有错误的前缀{_prefix}')
        input()
        raise ValueError

class Song:
    # 输入参数 av号/bv号/标题(不含av bv)  flag:0为bv,1为av,2为标题(返回第一个搜索结果)

    def __init__(self, av_bv, flag):
        res2 = get_info(av_bv, flag)
        try:
            da = res2['data']
            self.state = 1
            self.bvid = da['bvid'][2:]
            self.aid = str(da['aid'])
            self.stat = da['stat']
            self.stat_chinese = {
                Translate[i]: self.stat[i]
                for i in
                filter(lambda key: key in Translate, self.stat)
            }
            self.title = validateTitle(da['title'])
            self.pubdate = time.gmtime(int(da['pubdate']))
            self.pubdate_text = time.strftime('%Y/%m/%d %H:%M', time.gmtime(int(da['pubdate'])))
            self.pubdate_to_now = time.time() - da['pubdate']
            self.copyright = da['copyright']
            self.up = validateTitle(da['owner']['name'])
            self.desc = da['desc']
            self.staff = collect_staff.collect_staff(self.desc)
            self.vocal = ''
            for i in vocal_list:
                if i == '星尘':
                    ii = '星尘(?!Minus|minus|版)'
                else:
                    ii = i + '(?!版)'
                if re.search(r'' + ii, self.title, re.I) or re.search(r'' + ii, self.desc, re.I):
                    self.vocal += i + ','
            self.vocal = self.vocal[:-1]
        except KeyError:
            self.state = 0

    def renew_stat(self):
        res2 = requests.get('https://api.bilibili.com/x/web-interface/view?aid=' + str(self.aid))
        res2 = json.loads(res2.text)
        self.stat = res2['data']['stat']

    def download_cover(self, folder_path):
        # 下载视频封面，存储在folder_path，文件名为‘AVxxxxxxxx.jpg'
        aid = self.aid
        url = request('https://api.bilibili.com/x/web-interface/search/all?keyword=' + str(aid))
        url = json.loads(url.text)
        for i in url['data']['result']['video']:
            if str(i['id']) == str(aid):
                url = i['pic']
                break
        if url:
            pic = request('http:' + url)
            img_name = folder_path + 'AV' + str(aid) + '.jpg'
            with open(img_name, 'wb') as file:
                file.write(pic.content)
                file.flush()
                file.close()

    def __str__(self):
        """输出格式为:"av... BV... ...(标题)"""
        return f"av{self.aid}  BV{self.bvid}  {self.title}"
