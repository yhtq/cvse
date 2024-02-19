import datetime
from functools import lru_cache
import json
import os
import time
from io import BytesIO
from typing import Union, Optional, Callable

import requests
from PIL import Image

bilibili_headers: dict[str, str] = {
    'Host': 'www.bilibili.com',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54",
    "Referer": "https://www.bilibili.com"
}

default_headers : dict[str, str] = {
        'Host': 'api.bilibili.com',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54",
        "Referer": "https://www.bilibili.com"
    }

s = requests.session()
s.get('https://www.bilibili.com', headers=bilibili_headers, timeout=5)
def request(url: str, headers: dict[str, str] = None):
    try:
        if headers is None:
            res = s.get(url, timeout=5)
        else:
            res = s.get(url, headers=headers, timeout=5)
        if res.status_code == 412:
            print('请求被拦截')
            time.sleep(60)
            s.get('https://www.bilibili.com', headers=bilibili_headers, timeout=5)
            raise requests.RequestException
        res.raise_for_status()
    except requests.RequestException as e:
        print(e)
        time.sleep(1)
        print('尝试重新连接')
        return request(url)
    return res

@lru_cache(maxsize=128)
def request_with_default_headers(url: str):
    return request(url, headers=default_headers)

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
    res = request_with_default_headers('https://api.bilibili.com/x/web-interface/view?aid=' + str(aid))
    res = json.loads(res.text)
    cover_flag = 0
    address = res['data']['pic']
    pic = request(str(address))
    #with open(img_name, 'wb+') as file:
    #    file.write(pic.content)
    #    file.flush()
    #    file.close()
    #time.sleep(0.5)
    img: Image.Image = Image.open(BytesIO(pic.content))
    return img


@download_decorator
def download_face(mid: Union[int, str], img_name: str, time_sleep: float, with_save: bool = True) -> Image.Image:
    res = request_with_default_headers('https://api.bilibili.com/x/space/acc/info?mid=' + str(mid))
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
#download_cover(2231425, img_name='test.jpg', time_sleep=0.1, with_save=True)
if __name__ == '__main__':
    import csv
    #time.sleep(6000)
    data_path = "/home/yhtq/学习/cover/video.csv"
    with open(data_path, 'r', encoding='utf-8-sig') as file:
        dict_reader = csv.DictReader(file)
        result: list[dict] = []
        i: int = 0
        for row in dict_reader:
            i += 1
            if i >= 31:
                download_cover(row['aid'], f'/home/yhtq/学习/cover/{row["aid"]}.jpg', 10)
            data = res = request_with_default_headers('https://api.bilibili.com/x/web-interface/view?aid=' + str(row['aid']))
            res = json.loads(res.text)
            if int(res['code']) != 0:
                result.append({'aid': row['aid'], 'owner_name': '--', 'owner_mid': '--'})
                continue
            result.append({'aid': row['aid'], 'owner_name': res['data']['owner']['name'], 'owner_mid': res['data']['owner']['mid']})
            print(i)
    with open ('/home/yhtq/学习/cover/video_result.csv', 'w', encoding='utf-8') as file:
        dict_writer = csv.DictWriter(file, fieldnames=['aid', 'owner_name', 'owner_mid'])
        dict_writer.writeheader()
        dict_writer.writerows(result)

76
        
