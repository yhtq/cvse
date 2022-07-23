from PIL import Image, ImageDraw, ImageFont
import csv, json

from PIL.ImageFont import FreeTypeFont

img_long = Image.open('background/pic_long.png').convert('RGBA')
img_new = Image.open('background/pic_new.png').convert('RGBA')

with open('config_side.ini') as config_file:
    config = json.load(config_file)
    config_font = config['font_config']

def load_font(fontInfo):
    font = ImageFont.truetype(fontInfo[0], fontInfo[1])
    return font

font_num_rank = load_font(config_font['font_num_rank'])
font_num_data = load_font(config_font['font_num_data'])
font_num_av = load_font(config_font['font_num_av'])
font_num_corr = load_font(config_font['font_num_corr'])
font_num_pt = load_font(config_font['font_num_pt'])
font_last_pt = load_font(config_font['font_last_pt'])
font_title = load_font(config_font['font_title'])
font_up_date = load_font(config_font['font_up_date'])
font_last_rank = load_font(config_font['font_last_rank'])

header = {'名次': 0, '上次': 1, 'aid': 2, '标题': 3, 'mid': 4, 'up主':5,
          '投稿时间': 6, '时长': 7, '分P数': 8, '播放增量': 9, '弹幕增量': 10,
          '评论增量': 11, '收藏增量': 12, '硬币增量': 13, '分享增量': 15, '点赞增量': 14,
          'Pt': 16, '修正A': 17, '修正B': 18, '修正C': 19, 'Last Pt': 20, 'rate': 21, '长期': 22,
          'Nrank':23}

black = (0x40,0x40,0x40,255)
white = (255,255,255,255)
theme_dark = (0x59,0x59,0x59,255)
color_new = (0x60,0x9a,0xa6,255)
color_up = (0xd0,0x50,0x56,255)
color_down = (0x75,0x86,0x77,255)
color_eq = (0x58,0x63,0x71,255)

while True:
    try:
        mode = int(input('输入使用模式：1=SV榜，2=国产榜 3=UTAU榜\n'))
        if mode in (1,2,3):
            break
        else:
            print('格式错误!')
    except ValueError:
        print('格式错误!')

if mode == 1:
    theme = (0xa0,0xa7,0x76,255)
    bg_public = Image.open('background/side_public_SV.png').convert('RGBA')
    bg_single = Image.open('background/side_single_SV.png').convert('RGBA')
if mode == 2:
    theme = (0xf6, 0x97, 0x63, 255)
    bg_public = Image.open('background/side_public_C.png').convert('RGBA')
    bg_single = Image.open('background/side_single_C.png').convert('RGBA')
if mode == 3:
    theme = (0x75, 0x86, 0x77, 255)
    bg_public = Image.open('background/side_public_U.png').convert('RGBA')
    bg_single = Image.open('background/side_single_U.png').convert('RGBA')


def make_image_single(row:list)->Image.Image:
    bg = bg_single.copy()
    brush = ImageDraw.Draw(bg)
    #名次#上次
    if row[header['上次']].upper() == 'NEW':
        #NEW
        brush.text((config['rank_x'] - font_num_rank.getsize(row[header['名次']])[0] // 2, config['rank_y']),
                   row[header['名次']], fill=color_new, font=font_num_rank)
        brush.text((config['lastrank_x'] - font_last_rank.getsize('N E W')[0]//2, config['lastrank_y']), 'N E W',
                   fill=color_new, font=font_last_rank)
        bg.alpha_composite(img_new,(config['pic_x'],config['pic_y']))
        brush.text((config['pic_text_x'] - font_num_av.getsize(row[header['Nrank']])[0]//2, config['pic_text_y']),
                   row[header['Nrank']], fill=(0x4c, 0xbf, 0xee, 255), font=font_num_av)
    elif row[header['上次']] == '——':
        #▲ 上次：——
        brush.text((config['rank_x'] - font_num_rank.getsize(row[header['名次']])[0] // 2, config['rank_y']),
                   row[header['名次']], fill=color_up, font=font_num_rank)
        brush.text((config['lastrank_x'] - font_last_rank.getsize('▲ 上次：'+row[header['上次']])[0]//2,config['lastrank_y']),
                   '▲ 上次：'+row[header['上次']], fill=color_up, font=font_last_rank)
    elif row[header['名次']] == row[header['上次']]:
        #● 上次：xx
        brush.text((config['rank_x'] - font_num_rank.getsize(row[header['名次']])[0] // 2, config['rank_y']),
                   row[header['名次']], fill=color_eq, font=font_num_rank)
        brush.text((config['lastrank_x'] - font_last_rank.getsize('● 上次：' + row[header['上次']])[0]//2, config['lastrank_y']),
                   '● 上次：' + row[header['上次']], fill=color_eq, font=font_last_rank)
    elif row[header['上次']].upper().startswith('HOT') or int(row[header['名次']].replace(',','')) > int(row[header['上次']].replace(',','')):
        #▼ 上次：xx
        brush.text((config['rank_x'] - font_num_rank.getsize(row[header['名次']])[0] // 2, config['rank_y']),
                   row[header['名次']], fill=color_down, font=font_num_rank)
        brush.text((config['lastrank_x'] - font_last_rank.getsize('▼ 上次：' + row[header['上次']])[0]//2, config['lastrank_y']),
                   '▼ 上次：' + row[header['上次']], fill=color_down, font=font_last_rank)
    elif int(row[header['名次']].replace(',','')) < int(row[header['上次']].replace(',','')):
        #▲ 上次：xx
        brush.text((config['rank_x'] - font_num_rank.getsize(row[header['名次']])[0] // 2, config['rank_y']),
                   row[header['名次']], fill=color_up, font=font_num_rank)
        brush.text((config['lastrank_x'] - font_last_rank.getsize('▲ 上次：' + row[header['上次']])[0]//2, config['lastrank_y']),
                   '▲ 上次：' + row[header['上次']], fill=color_up, font=font_last_rank)
    #标题
    brush.text((config['title_x'], config['title_y']), row[header['标题']], fill=theme_dark, font=font_title)
    #播放量
    brush.text((config['play_x'], config['play_y']), row[header['播放增量']], fill=black, font=font_num_data)
    #分享
    brush.text((config['share_x'], config['share_y']), row[header['分享增量']], fill=black, font=font_num_data)
    #点赞
    brush.text((config['like_x'], config['like_y']), row[header['点赞增量']], fill=black, font=font_num_data)
    #修正A
    brush.text((config['corrA_x'], config['corrA_y']), row[header['修正A']], fill=theme, font=font_num_corr)
    #收藏
    brush.text((config['favorite_x'], config['favorite_y']), row[header['收藏增量']], fill=black, font=font_num_data)
    #硬币
    brush.text((config['coin_x'], config['coin_y']), row[header['硬币增量']], fill=black, font=font_num_data)
    #修正B
    brush.text((config['corrB_x'], config['corrB_y']), row[header['修正B']], fill=theme, font=font_num_corr)
    #评论
    brush.text((config['comment_x'], config['comment_y']), row[header['评论增量']], fill=black, font=font_num_data)
    #弹幕
    brush.text((config['danmu_x'], config['danmu_y']), row[header['弹幕增量']], fill=black, font=font_num_data)
    #修正C
    brush.text((config['corrC_x'], config['corrC_y']), row[header['修正C']], fill=theme, font=font_num_corr)
    #Pt
    brush.text((config['Pt_x']-font_num_pt.getsize(row[header['Pt']])[0], config['Pt_y']),
               row[header['Pt']], fill=black, font=font_num_pt)
    #LastPt#Rate
    if row[header['上次']] != 'NEW' and row[header['上次']] != '——':
        brush.text((config['LastPt_x'] - font_last_pt.getsize('Last Pt. ' + row[header['Last Pt']])[0], config['LastPt_y']),
                   'Last Pt. ' + row[header['Last Pt']], fill=black, font=font_last_pt)
        brush.text((config['rate_x'] - font_last_pt.getsize('Rate. ' + row[header['rate']])[0], config['rate_y']),
                   'Rate. ' + row[header['rate']], fill=black, font=font_last_pt)
    else:
        brush.text((config['LastPt_x'] - font_last_pt.getsize('Last Pt. ——')[0], config['LastPt_y']),
                   'Last Pt. ——', fill=black, font=font_last_pt)
        brush.text((config['rate_x'] - font_last_pt.getsize('Rate. ' + row[header['rate']])[0], config['rate_y']),
                   'Rate. ' + row[header['rate']], fill=black, font=font_last_pt)

    #aid
    brush.text((config['aid_x'] - font_num_av.getsize('av' + row[header['aid']])[0] // 2, config['aid_y']),
               'av' + row[header['aid']], fill=white, font=font_num_av)
    #UP主
    brush.text((config['UP_x'], config['UP_y']), row[header['up主']] + " 投稿", fill=theme_dark, font=font_up_date)
    #投稿时间
    brush.text((config['UP_x']+font_up_date.getsize(row[header['up主']]+' 投稿        ')[0], config['UP_y']),
               'Date. '+row[header['投稿时间']], fill=theme_dark, font=font_up_date)
    #封面图
    try:
        cover = Image.open('side_cover/AV'+row[header['aid']]+'.jpg').convert('RGBA')
        bg.alpha_composite(cover.resize((config['cover_size_x'],config['cover_size_y'])),
                           (config['cover_loc_x'],config['cover_loc_y']))
    except FileNotFoundError:
        print('缺失'+row[header['名次']]+'位投稿封面！')
    except OSError:
        print(row[header['名次']]+'位投稿封面损坏！')

    #头像图
    try:
        icon = Image.open('side_cover/uid'+str(row[header['mid']])+'-'+row[header['up主']]+'.jpg')
        icon_reshaped = icon.resize((config['icon_size_x'],config['icon_size_y']))
        mask = Image.new('L',(config['icon_size_x'],config['icon_size_y']),0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0,0,config['icon_size_x'],config['icon_size_y']),fill=255)
        icon_reshaped.putalpha(mask)
        bg.alpha_composite(icon_reshaped, (config['icon_loc_x'],config['icon_loc_y']))

    except FileNotFoundError:
        print('缺失' + row[header['名次']] + '位投稿UP主头像！')
    except OSError:
        print(row[header['名次']] + '位投稿UP主头像损坏！')
    except:
        print(row[header['名次']])
    #长期,若有
    if row[header['长期']] != '':
        bg.alpha_composite(img_long,(config['pic_x'],config['pic_y']))
        brush.text((config['pic_text_x'] - font_last_rank.getsize(row[header['长期']])[0] // 2, config['pic_text_y']),
                   row[header['长期']], fill=(0xff, 0x7a, 0x60, 255), font=font_num_av)

    return bg

while True:
    try:
        num_start = int(input('输入副榜的起始名次\n'))
        break
    except ValueError:
        print('格式错误!')

while True:
    try:
        num_end = int(input('输入副榜的结束名次\n'))
        break
    except ValueError:
        print('格式错误!')
try:
    with open('outfile.csv', 'r') as outfile:
        out_reader = csv.reader(outfile)
        out_list = [row for row in out_reader]
except UnicodeDecodeError:
    with open('outfile.csv', 'r',encoding='utf-8') as outfile:
        out_reader = csv.reader(outfile)
        out_list = [row for row in out_reader]

if out_list[0][0] == '名次' or out_list[0][0] == '\ufeff名次':del out_list[0]

num_HOT = 0
rank_new = 0
for row in out_list:
    if row[header['名次']].startswith('HOT'): num_HOT+=1
    else: break

for row in out_list:
    row[header['Pt']] = '{:.0f}'.format(float(row[header['Pt']]))
    row[header['Pt']] = '{:,}'.format(int(row[header['Pt']]))
    row[header['播放增量']] = '{:,}'.format(int(row[header['播放增量']]))
    row[header['收藏增量']] = '{:,}'.format(int(row[header['收藏增量']]))
    row[header['分享增量']] = '{:,}'.format(int(row[header['分享增量']]))
    row[header['点赞增量']] = '{:,}'.format(int(row[header['点赞增量']]))
    row[header['评论增量']] = '{:,}'.format(int(row[header['评论增量']]))
    row[header['弹幕增量']] = '{:,}'.format(int(row[header['弹幕增量']]))
    row[header['硬币增量']] = '{:,}'.format(int(row[header['硬币增量']]))
    row[header['修正A']] = '{:.3f}'.format(float(row[header['修正A']]))
    row[header['修正B']] = '{:.3f}'.format(float(row[header['修正B']]))
    row[header['修正C']] = '{:.3f}'.format(float(row[header['修正C']]))
    try:
        row[header['rate']] = "{:.3f}".format(float(row[header['rate']]) * 100) + "%"
    except ValueError:
        pass
    try:
        row[header['Last Pt']] = '{:,}'.format(int(row[header['Last Pt']]))
    except ValueError:
        pass
    while len(row) <= header['Nrank']: row.append('')
    if row[header['长期']] != '': row[header['长期']] = row[header['长期']].zfill(2) + r' / 10'
    if row[header['Nrank']] != '': row[header['Nrank']] = row[header['Nrank']].zfill(3).replace('', ' ')[1:-1]





list_image_single = []

for i in range(num_start+num_HOT-1,num_end+num_HOT):
    row = out_list[i]
    list_image_single += [make_image_single(row)]
    #print("正常:"+str(i)+"号第"+str(row[header['名次']])+"位")

for i in range(0,len(list_image_single),3):
    img = bg_public.copy()
    try:
        img.alpha_composite(list_image_single[i], dest=(0, 29))
        img.alpha_composite(list_image_single[i + 1], dest=(0, 362))
        img.alpha_composite(list_image_single[i + 2], dest=(0, 708))
    except IndexError:
        pass
    img.save('side/'+str(i+num_start)+'.png')

list_image_single_new = []

for row in out_list[num_end+num_HOT:]:
    if row[header['上次']].upper() == 'NEW':
        list_image_single_new += [make_image_single(row)]

for i in range(0,len(list_image_single_new),3):
    img = bg_public.copy()
    try:
        img.alpha_composite(list_image_single_new[i], dest=(0, 29))
        img.alpha_composite(list_image_single_new[i + 1], dest=(0, 362))
        img.alpha_composite(list_image_single_new[i + 2], dest=(0, 708))
    except IndexError:
        pass
    img.save('side/new_'+str(i)+'.png')







