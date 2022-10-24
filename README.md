# 简介

> 生成的同一大小文件内容是相同的（重复文件）

用于自动造文件并push到设备指定路径

可以用于生成mp4、mp3、以及其它自定义格式 MP4 MP3 不支持指定大小

如果出现问题 请尝试升级pip版本 `python3 -m pip install --upgrade pip `

# 使用方法

> 本脚本可以用于自动造文件并push到设备指定路径

1. 必须使用**Python3**
2. **连接设备只能有一个** (adb devices 可查看)
3. **在config.txt中配置**：
  例子：largeFile[0-9]{4}\.txt->/sdcard/Download/->false->10->10240 
  通过->区分参数

- 正则表达式（文件名)
- 要push到的设备路径(如果含有正则表达式或者空格记得加\转义符)
- 设备路径是否含有正则表达式(是填true 否则填false)
- 生成的文件数量(整数)
- 每个文件至少多少KB(越小生成越快 不在意大小的话直接填0.001即1byte即可)
  (config.txt中可以使用#开头隐藏该行配置)

4. 在bin目录下（必须） 执行命令 python3 ProductFiles.py 即可生效
  如果是python只安装了一个版本 则直接使用python ProductFiles.py
