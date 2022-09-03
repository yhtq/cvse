import CVSE_Data
import json
import os
import subprocess
import csv

status = 1
try:
    with open("config_inclusion.ini", 'r', encoding='utf-8') as f:
        config = json.load(f)
        TEditor: str = config['TEditor']
        ted_path: dict[str, str] = {i: j for i, j in config['ted_path'].items()}
        TEditor_dir, _ = os.path.split(TEditor)
        if not os.path.exists(TEditor):
            raise "没有找到TEditor"
except Exception as e:
    status = 0
    print(e)
    print('模板生成配置错误')


def generate(data: list[CVSE_Data.Data],
             ted_type: str,
             csv_header: list[str],
             out_path: str = TEditor_dir,
             end_flag: tuple[str, str] = None,
             valid: callable(CVSE_Data.Data) = lambda x: True):
    # 调用TEditor生成模板，ted_type是类型（需要调用的ted文件类型），path是生成模板存放目录（可以使相对主目录路径或绝对路径），end_flag是(key,value)，表示生成截止到data[key]==value时
    TEditor = config['TEditor']
    if not status:
        return
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    print(f'正在生成{ted_type}模板')
    if ted_type not in ted_path.keys():
        print("没有找到ted文件")
        return
    temp_writer, save = CVSE_Data.Data.write_to_csv_wrapper(os.path.join(TEditor_dir, "temp.csv"), _header=csv_header)
    count: int = 0
    for i in data:
        if not valid(i):
            continue
        temp_writer(i, with_format=True)
        count += 1
        if end_flag is not None:
            if i[end_flag[0]] == end_flag[1]:
                break
    save()
    out_path = os.path.abspath(out_path)
    ted_path[ted_type] = os.path.abspath(ted_path[ted_type])
    data_path = os.path.abspath(os.path.join(TEditor_dir, "temp.csv"))
    TEditor = os.path.abspath(TEditor)
    pres_path = os.path.abspath(os.getcwd())
    os.chdir(TEditor_dir)
    try:
        args = [TEditor,
                "batchgen",
                '-d', data_path,
                '-i', ted_path[ted_type],
                '-o', out_path,
                '-n', ted_type + '_{index}',
                '-s', '1',
                '-e', str(count)]
        if ted_type == 'new_side':
            args += ['-r', '5', '-y', '163']
        #print(args)
        subprocess.run(args,
                       stdout=subprocess.PIPE,
                       encoding='gbk'
                       )
    except subprocess.CalledProcessError as e:
        print(e)
        print("模板生成失败")
        return
    finally:
        os.remove(data_path)
        pass
    os.chdir(pres_path)
    print(f'{ted_type}模板生成完成')
    return
