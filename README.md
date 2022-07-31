# CVSE
 收录/制作模板用
 
 暂时是个可能稳定的版本，后续还有很多东西没改
 
 cvse_新.py/cvse_新.exe是要运行的脚本
 
 CVSE_Data.py主要是按照CVSE常用格式读写数据，不需要运行
 
 match.py主要由JackBlock老师和旭东丸老师完成，用于判断长期/HOT以及与上期数据匹配，这里已经做了整合不需要单独运行
 
 C_60 C_61是两个已经完成的收录工程样例

 config_inclusion.ini中设置了主副榜，新曲榜个数以及是否匹配上期数据，是否抄写staff


 使用方法（以国产榜61期为例）：
 
 1.更新主目录下data_C.xlsx，用于判断长期/HOT（SV/U则更新对应文件）(不启用匹配时不需要)
 
 2.在cvse_新.py同目录下新建文件夹C_61 （SV刊则为SV_61)，以下所有数据均放在此文件夹
 
 3.下载61期原始数据文件或者完成收录的数据文件，csv或xlsx均可，列索引按照CVSE通常格式（具体暂时可以参照CVSE_Data.py，以后会完善），已经完成的收录文件要求按照CVSE规范涂色（不要求涂哪一列）
 
 4.下载61期对应历史回顾49期的数据表(不制作回顾环节则不需要)

 5.下载上一期60期已经完成的数据表，也可以是由本脚本生成的数据表，csv或xlsx均可，放在C_60文件夹中（不启用匹配时不需要）
 
 5.运行cvse_新.py或cvse_新.exe
 
 6.按照提示运行即可。关于保存机制，完成一首曲子的收录后会自动保存记录于C_61_save.csv，下次收录同一期的时候会读取进度。如果出现手误需要手动修改C_61_save.csv并重新运行。
 
 7.完成后会在C_61文件夹下生成若干数据文件（注意主目录的remove.txt是所有被排外的视频的aid，需要提交的当期被排外的视频aid是当前目录下的remove_61.txt），自动下载主榜封面和历史回顾排行榜封面于cover文件夹，副榜封面与所有头像于side_cover文件夹，并更新主目录下data_C.xlsx与remove.txt
 
 （ps.如要制作模板，使用TEditor记得修改模板路径；制作副榜模板要将outfile.csv移至主目录下，相关封面/头像路径无需调整）



 已知问题：
 
 1.数据信息中曲目数的差值（比如新曲/原创曲数量较上期变化值）是错误的
 
 2.从简介提取staff功能目前还是由一个拍脑门写出来的正则表达式完成，正确率并不高
 
 3.输入staff环节没有设计空staff（比如翻调曲目全部由up主完成时应跳过staff）暂时可以用输入空格替代
 
 

 TODO:
 
 1.U刊相关功能
 
 2.将主榜数量，数据表表头等配置参数独立出脚本
 
 3.staff提取相关完善（还没想好怎么改x）
 
 4.头像/封面下载改成异步逻辑（当前收录两个视频之间会感觉到一些卡顿，部分由于当初设计时高估了下载图片的速度x
 
 5.添加更方便的改错机制（还没想好怎么改x）
 
 6.UI相关（暂时还没啥想法应该做不出来x
