import datetime
import json
import time
import openpyxl
import CVSE_Data

header = {'名次': 0, '上次': 1, 'aid': 2, '标题': 3, 'mid': 4, 'up主': 5,
          '投稿时间': 6, '时长': 7, '分P数': 8, '播放增量': 9, '弹幕增量': 10,
          '评论增量': 11, '收藏增量': 12, '硬币增量': 13, '分享增量': 14, '点赞增量': 15,
          'Pt': 16, '修正A': 17, '修正B': 18, '修正C': 19, 'Last Pt': 20, 'rate': 21}

with open('config_match.ini') as config_file:
    config = json.load(config_file)


# 判断长期，鸣谢：JackBlock
# yhtq 修改


def match(rank: int, index: int, start_time: datetime.datetime, pres_list: list[CVSE_Data.Data], prev_list: list[CVSE_Data.Data]):
    list_long = {}
    rank_trans = {0: "C", 1: "SV", 2: "U"}
    conti_bound = config[f'continuous_ranked_time_bound_{rank_trans[rank]}']
    nonconti_bound = config[f'non_continuous_ranked_time_bound_{rank_trans[rank]}']
    nonconti_enter = config[f'non_continuous_long_enter_bound_{rank_trans[rank]}']
    nonconti_leave = config[f'non_continuous_long_leave_bound_{rank_trans[rank]}']
    # 读取表格
    workbook = openpyxl.load_workbook(f'data_{rank_trans[rank]}.xlsx')
    worksheet = workbook.active
    table = []
    for col in worksheet.iter_cols():
        if col[0].value == f'#{index}':
            break
        table.append([str(cell.value) for cell in col])
    songs = []  # 输出用列表
    songs1 = []  # 录入用列表
    songs2 = []  # 筛选用列表
    hot = {}
    # 录入数据
    for col in table:  # 准备判断HOT
        for line_index in range(0, len(col)):
            if table[0][line_index] == 'HOT':
                hot[col[line_index]] = 2
            if table[0][line_index] in ['1', '2', '3']:
                if col[line_index] in hot.keys():
                    hot[col[line_index]] = 2  # 已经两次进入前三
                else:
                    hot[col[line_index]] = 1
    for col in table[1:]:
        for av in col[1:]:
            if not av.isdigit():
                continue
            songs1 += [av]
    # 获取所有入榜次数大于等于conti_bond或nonconti_enter期,即有可能进入过长期的歌曲
    for av in songs1:
        if songs1.count(av) >= min(conti_bound, nonconti_enter) and av not in songs2:
            songs2 += [av]
    for av in songs2:
        # 初始化
        count_all = songs1.count(av)  # 全部入榜期数
        count_sum = 0  # 长期论外期数
        count_in = 0  # 长期论外期内入榜期数
        count_in_rec = 0  # nonconti_bound期内入榜期数
        count_out_rec = 0  # nonconti_bound期内出榜期数
        count_continuous_in = 0  # 连续入榜期数
        count_continuous_out = 0  # 连续出榜期数
        col = 0  # 表格列标记
        first_in = ""  # 长期论外期内首次入榜期
        # 判断
        while col <= len(table) - 2:
            col += 1
            # 入榜判断
            if av in table[col][1:] or str(av) in table[col][1:]:
                # 入榜处理
                if first_in == "":
                    first_in = str(table[col][0])
                count_in += 1
                count_continuous_in += 1
                count_continuous_out = 0
                if count_in_rec + count_out_rec < nonconti_bound:
                    count_in_rec += 1
                else:
                    if av not in table[col - nonconti_bound][1:]:
                        count_in_rec += 1
                        count_out_rec -= 1
            else:
                # 出榜处理
                if count_in == 0:
                    continue
                count_continuous_out += 1
                count_continuous_in = 0
                if count_in_rec + count_out_rec < nonconti_bound:
                    count_out_rec += 1
                else:
                    if av in table[col - nonconti_bound][1:]:
                        count_out_rec += 1
                        count_in_rec -= 1
            count_sum += 1
            # 长期论外脱落判断
            if count_out_rec >= nonconti_leave:
                if av in songs:
                    songs.remove(av)
                # 判断剩余入榜期数是否达到最低要求期,即是否有再一次进入长期的可能
                if count_all - count_in < min(conti_bound, nonconti_enter):
                    break
                else:
                    # 初始化
                    count_all -= count_in
                    count_sum = 0
                    count_in = 0
                    count_continuous_out = 0
                    count_continuous_in = 0
                    count_in_rec = 0
                    count_out_rec = 0
                    first_in = ""
                    continue
            # 长期论外达成
            if (count_in_rec >= nonconti_enter or count_continuous_in >= conti_bound) and av not in songs:
                songs.append(av)
            # 输出
            if col == len(table) - 1 and av in songs:
                list_long[int(av)] = count_in_rec

    """try:
        while True:
            try:
                start_time = time.strptime(input('请输入本期周刊的收录起始时间，格式为YYYY/M/D HH:MM\n'), '%Y/%m/%d %H:%M')
                break
            except ValueError:
                print('输入格式不正确！')
        try:
            with open('previous.csv', 'r') as prev:
                with open('present.csv', 'r') as pres:
                    pres_reader = csv.reader(pres)
                    prev_reader = csv.reader(prev)
                    pres_list = [row for row in pres_reader]
                    prev_list = [row for row in prev_reader]
                    del pres_list[0]
        except UnicodeDecodeError:
            with open('previous.csv', 'r', encoding='utf-8') as prev:
                with open('present.csv', 'r', encoding='utf-8') as pres:
                    pres_reader = csv.reader(pres)
                    prev_reader = csv.reader(prev)
                    pres_list = [row for row in pres_reader]
                    prev_list = [row for row in prev_reader]
                    del pres_list[0]
        """
    i = 0
    for row_pres in pres_list:
        i += 1
        for row_prev in prev_list:
            # 匹配并计算相关数据
            #if row_pres[header['aid']] == row_prev[header['aid']]:
            if row_pres.is_same_song(row_prev):
                row_pres[header['上次']] = row_prev[header['名次']]
                row_pres[header['Last Pt']] = row_prev[header['Pt']]
                row_pres.add_info(row_prev, key='staff')
                row_pres.add_info(row_prev, key='原创')
                row_pres.add_info(row_prev, key='引擎')
                if float(row_pres[header['Last Pt']]) != 0.0:
                    row_pres[header['rate']] = (
                            (float(row_pres[header['Pt']]) / float(row_pres[header['Last Pt']])) - 1).__round__(
                        5)
                else:
                    row_pres[header['rate']] = '——'
                break
        if row_pres[header['上次']] == '' or row_pres[header['上次']] == 'NEW':
            row_pres[header['Last Pt']] = '——'
            post_time = row_pres.pub_time_datetime
            """try:
                post_time = time.strptime(row_pres[header['投稿时间']], '%Y/%m/%d %H:%M')
            except ValueError:
                post_time = time.strptime(row_pres[header['投稿时间']], '%Y-%m-%d %H:%M')
                row_pres[header['投稿时间']] = time.strftime('%Y/%m/%d %H:%M', post_time)"""
            row_pres[header['投稿时间']] = time.strftime('%Y/%m/%d %H:%M', row_pres.pub_time_time_struct)
            if post_time > start_time:
                row_pres[header['上次']] = 'NEW'
                row_pres[header['rate']] = 'NEW!'
            else:
                row_pres[header['上次']] = '——'
                row_pres[header['rate']] = '——'
        # 判断长期入榜
        aid = row_pres[header['aid']]
        if aid in list_long:
            recent_in = list_long[aid]
            row_pres['长期入榜及期数'] = recent_in
        _hot = 0
        if str(aid) in hot.keys():
            _hot = hot[str(aid)]
        if _hot == 2:
            row_pres['HOT'] = '两次前三'

        if i % 100 == 0:
            print('正在处理第' + str(i) + '/' + str(len(pres_list)) + '条记录……')


"""    while True:
        try:
            with open('outfile.csv', 'w', newline='', encoding='utf-8') as outfile:
                outfile_writer = csv.writer(outfile)
                outfile_writer.writerow(['\ufeff名次', '上次', 'aid', '标题', 'mid', 'up主', '投稿时间', '时长', '分P数',
                                         '播放增量', '弹幕增量', '评论增量', '收藏增量', '硬币增量', '分享增量', '点赞增量',
                                         'Pt', '修正A', '修正B', '修正C', 'Last Pt', 'rate', '长期入榜及期数'])
                outfile_writer.writerows(pres_list)
                break
        except PermissionError:
            print("输出文件被占用，请关闭Excel窗口后重试！")
            input('按下Enter键以继续……')"""
