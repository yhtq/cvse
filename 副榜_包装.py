# 包装副榜生成器实现直接传参
import os
import shutil


def side_generate(*args):
    # 三个参数依次是排行榜类型，副榜起始名次，副榜结束名次
    i = iter(args)

    def input(text: str):
        # 重写input方法覆盖code中的input
        return next(i)

    with open("副榜.py", 'r', encoding='utf-8') as f:
        code = f.read()
    try:
        exec(code, locals(), locals())
    except ValueError as e:
        print(e)
        print('副榜模板生成中断')
    return


def move_file(ori_path: str, target_dir: str):
    # 移动生成的模板
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    file_list: list[str] = os.listdir(ori_path)
    for file in file_list:
        if file == '.gitkeep':
            continue
        ori = os.path.join(ori_path, file)
        tar = os.path.join(target_dir, file)
        shutil.move(ori, tar)


def remove_file(path: str):
    # 删除文件夹下所有文件
    file_list: list[str] = os.listdir(path)
    for file in file_list:
        if file == '.gitkeep':
            continue
        try:
            os.remove(os.path.join(path, file))
        except PermissionError as e:
            shutil.rmtree(os.path.join(path, file))
            continue
