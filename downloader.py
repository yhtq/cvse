import datetime
import json
import os
import time
from io import BytesIO
from typing import Union, Optional, Callable

import requests
from PIL import Image


def request(url: str, headers: dict[str, str] = None):
    try:
        if headers is None:
            res = requests.get(url, timeout=5)
        else:
            res = requests.get(url, headers=headers, timeout=5)
        res.raise_for_status()
    except requests.RequestException as e:
        print(e)
        time.sleep(1)
        print('尝试重新连接')
        return request(url)
    return res


def download_decorator(func: Callable[[Union[int, str], str, float, bool], Image.Image]) \
        -> Callable[[Union[int, str], str, float, bool], Optional[Image.Image]]:
    def download(aid_mid: Union[int, str], img_name: str, time_sleep: float, with_save: bool = True) -> Optional[Image.Image]:
        if os.path.exists(img_name):
            return None
        if aid_mid == '':
            print(img_name + ' 为空')
            return None
        try:
            img: Image = func(aid_mid, img_name, time_sleep, with_save)
            time.sleep(time_sleep)
            img.convert('RGB')
            if with_save:
                img.save(img_name)
            return img
        except Exception as e:
            print(e)
            print(img_name + '下载失败')
            return None
    return download


@download_decorator
def download_cover(aid: Union[int, str], img_name: str, time_sleep: float, with_save: bool = True) -> Image.Image:
    res = request('https://api.bilibili.com/x/web-interface/search/all?keyword=' + str(aid))
    res = json.loads(res.text)
    cover_flag = 0
    address = res['data']['result']['video'][0]['pic']
    pic = request('http:' + str(address))
    #with open(img_name, 'wb+') as file:
    #    file.write(pic.content)
    #    file.flush()
    #    file.close()
    #time.sleep(0.5)
    img: Image.Image = Image.open(BytesIO(pic.content))
    return img


@download_decorator
def download_face(mid: Union[int, str], img_name: str, time_sleep: float, with_save: bool = True) -> Image.Image:
    headers: dict[str, str] = {
        'Host': 'api.bilibili.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'
    }
    res = request('https://api.bilibili.com/x/space/acc/info?mid=' + str(mid), headers=headers)
    res = json.loads(res.text)
    address = res['data']['face']
    pic = request(str(address))
    #with open(img_name, 'wb+') as file:
    #    file.write(pic.content)
    #    file.flush()
    #    file.close()
    #time.sleep(0.5)
    return Image.open(BytesIO(pic.content))


def download_pres_data(end_time: datetime.datetime, rank: int, index: int, address: str) -> int:
    # 返回是否正常下载
    # 原始数据
    # 下载文件路径为 {address}/{index}.csv
    if os.path.exists(f'{address}/{index}.csv'):
        return 1
    trans = {0: 'domestic', 1: 'synthv'}
    name = f'{trans[rank]}增量_{end_time.strftime("%y%m%d")}.csv'
    print(f'正在下载{name}')
    res = requests.get(f'https://tombus.lty.fun/榜单数据/{trans[rank]}/{name}')
    try:
        res.raise_for_status()
    except requests.RequestException:
        print(f'{name}下载失败')
        return 0
    with open(f'{address}/{index}.csv', 'wb+') as file:
        file.write(res.content)
        file.flush()
    return 1


def download_history_data(end_time: datetime.datetime, rank: int, index: int, address: str) -> int:
    # 返回是否正常下载
    # 完成数据
    # 下载文件路径为 {address}/{index}.xlsx
    if os.path.exists(f'{address}/{index}.xlsx'):
        return 1
    if not os.path.exists(f'{address}'):
        os.makedirs(f'{address}')
    trans = {0: '月刊国产榜', 1: '周刊SynthV排行榜'}
    name = f"{index:03}.xlsx" if rank == 1 else f"{index}-{end_time.strftime('%y%m')}.xlsx"
    print(f'正在下载{name}')
    #print(f'https://data.cvse.cc/pub/{trans[rank]}/{end_time.strftime("%Y")}/{name}')
    res = requests.get(f'https://data.cvse.cc/pub/{trans[rank]}/{end_time.strftime("%Y")}/{name}')
    try:
        res.raise_for_status()
    except requests.RequestException:
        print(f'{name}下载失败')
        return 0
    with open(f'{address}/{index}.xlsx', 'wb+') as file:
        file.write(res.content)
        file.flush()
    return 1

#download_history_data(datetime.datetime.strptime('2101', '%y%m'), 1, 85, '.')
