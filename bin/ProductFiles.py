# -*- coding: UTF-8 -*-
# must use python3
# pip install xeger
import random
from InstallLibrary import install_libraries

install_libraries()

from xeger import Xeger
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import shutil
import subprocess
import sys
import cv2

# 每一行 正则表达式,存放路径,生成文件数量 注意使用英文的,区分
configPath = "./config.txt"
configParamsSize = 5
tempFolder = "./tempFolder"
tempImagePath = tempFolder + "/tempImage.png"
spliteSymbol = '->'
expressionList = []
pathList = []
sizeLit = []
perFileSizeList = []
# 存放tempFolderPath与要push路径的键值对
tempDict = {}
# 存放push成功的路径以及数量
successPushData = {}

ADB_ROOT = "adb root"
ADB_PUSH = "adb push  "
ADB_LS = "adb shell ls "
ADB_MKDIR = "adb shell mkdir "
ADB_NOTIFY_MEDIA = "adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://"


# 创建文件夹
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
        print("Info 创建文件夹 " + path)

    else:
        print("Info 已有文件夹 " + path + " 删除重置")
        shutil.rmtree(path)
        mkdir(path)


# push文件到设备指定路径
def pushToDevice(filePath, targetPath, fileName, pathIndex):
    cmd = ADB_PUSH + filePath + " " + targetPath
    realTargetPath = "\"" + targetPath + "\""
    isAlive = subprocess.getstatusoutput(ADB_LS + realTargetPath)
    if isAlive[0] == 1:
        resp = subprocess.getstatusoutput(ADB_MKDIR + realTargetPath)
        print("Warning 目标文件夹不存在 尝试创建  resp = " + str(resp))

    pushOK = subprocess.getstatusoutput(cmd)
    if pushOK[0] == 0:
        if successPushData.get(pathIndex):
            successPushData[pathIndex] = successPushData[pathIndex] + 1
        else:
            successPushData[pathIndex] = 1
        notifyMediaScanFiles(targetPath + fileName)


# 通知Media库更新文件
def notifyMediaScanFiles(filePath):
    result = subprocess.getstatusoutput(ADB_NOTIFY_MEDIA + filePath)
    if result[0] == 1:
        print("Warning updateMediaBroadcast fail " + filePath)


# 读取配置文件
def readConfig():
    global configPath
    global configParamsSize
    global spliteSymbol
    configFile = open(configPath, 'r')
    xegerS = Xeger()
    print("\nInfo 开始读取配置—————————————————————————————————————————————————————————————————————————————————————————————")
    for line in configFile.readlines():
        content = line.strip()
        if content == "":
            continue
        list = content.split(spliteSymbol)
        if line.startswith("#"):
            continue
        elif len(list) < configParamsSize:
            print("Warning 配置错误已忽略 " + str(line))
            continue
        expressionList.append(list[0])
        realPath = list[1]
        isPathExpression = list[2]
        if isPathExpression == "true":
            realPath = xegerS.xeger(list[1])
        pathList.append(realPath)
        sizeLit.append(list[3])
        perFileSizeList.append(list[4])
        print("Info 配置正确已加载 " + str(line))
    print("Info 配置文件读取完毕——————————————————————————————————————————————————————————————————————————————————————————\n")


# 根据正则表达式自动生成文件
def productFiles(index, expression):
    global sizeLit
    global pathList
    global tempFolder
    global perFileSizeList
    xegerS = Xeger()
    folderPath = tempFolder + "/" + str(index)
    mkdir(folderPath)
    tempDict[folderPath] = pathList[index]
    fileSize = perFileSizeList[index]
    curCount = int(sizeLit[index])
    for i in range(curCount):
        fileName = xegerS.xeger(expression)
        i += 1
        productFile(folderPath, fileName, float(fileSize))
        print("Info " + str(i) + "/" + str(curCount) + "文件已生成")


# 生成文件
def productFile(folderPath, fileName, fileSize):
    filePath = folderPath + "/" + fileName
    if filePath.endswith(".png") or filePath.endswith(".jpg"):
        print("Warning png图片无法设置大小 " + filePath)
        createImage(filePath)
        return
    elif filePath.endswith(".mp4"):
        print("Warning mp4视频无法设置大小 " + filePath)
        createVideo(filePath)
        return
    dataSize = 0
    targetSize = fileSize * 1024
    content = "content"
    with open(filePath, "w", encoding="utf8") as f:
        while dataSize < targetSize:
            if dataSize == 0 and targetSize > 1024 * 1024:
                baseSize = sys.getsizeof(content)
                content = content * (int(targetSize / baseSize))
            f.write(content)
            f.flush()
            dataSize = os.path.getsize(filePath)
            if targetSize > 1024 * 1024 * 10:
                print("Info " + filePath + "生成进度 " + str((dataSize / targetSize) / 1) + "%")


# push所有文件到指定路径
def pushAllFiles():
    global tempDict
    global pathList
    result = subprocess.getstatusoutput(ADB_ROOT)
    if result[0] == 1:
        print("Error root 设备失败 无法push文件")
        return
    print("Info root 设备成功")
    index = 0
    for key in tempDict:
        pushCount = 0
        allPushCount = len(os.listdir(key))
        curPathIndex = pathList.index(tempDict[key])
        for filename in os.listdir(key):
            filePath = key + "/" + filename
            targetPath = tempDict[key]
            pushToDevice(addEscape(filePath), targetPath, filename, curPathIndex)
            pushCount = pushCount + 1
            print("Info " + tempDict[key] + " push进度 " + str(pushCount) + "/" + str(allPushCount))
        index = index + 1
        print("Info " + tempDict[key] + " 文件夹所有文件push完毕")


# 自动转义
def addEscape(value):
    reserved_chars = r'''?&|!{}[]()^~*:\\"'+- '''
    replace = ['\\' + l for l in reserved_chars]
    trans = str.maketrans(dict(zip(reserved_chars, replace)))
    return value.translate(trans)


# 判断是否有重复正则表达式
def isAvailableTempDict():
    global tempDict
    global expressionList
    if len(expressionList) != len(tempDict):
        return False
    return True


def removeTempFolder():
    global tempFolder
    shutil.rmtree(tempFolder)
    print("Info 已删除temp文件夹")


def createImage(path):
    size = (360, 640)
    colorList = ["red", "blue", "green", "orange", "cyan", "purple"]
    curColor = random.choice(colorList)
    param = "RGBA"
    if path.endswith(".jpg"):
        param = "RGB"
    image = Image.new(param, size, curColor)
    image.save(path)


def getRandomImage():
    global tempImagePath
    size = (360, 640)
    colorList = ["red", "blue", "green", "orange", "cyan", "purple"]
    curColor = random.choice(colorList)
    param = "RGBA"
    image = Image.new(param, size, curColor)
    image.save(tempImagePath)


def createVideo(path):
    global tempImagePath
    fps = 16
    size = (360, 640)
    videowriter = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)

    for i in range(1, 50):
        getRandomImage()
        img = cv2.imread(tempImagePath)
        videowriter.write(img)


def displayResult():
    global successPushData
    colors = list(mcolors.TABLEAU_COLORS.keys())
    key = list(successPushData)
    value = list(successPushData.values())
    plt.bar(range(len(key)), value, color=colors, tick_label=key)
    plt.xlabel("Config index")
    plt.ylabel('The number of successful pushes to the configured target folder')
    plt.title('Result')
    plt.show()


def main():
    global tempFolder
    global expressionList
    global pathList
    global sizeLit
    readConfig()
    if len(expressionList) == 0:
        print("Info 无正确配置项 停止运行")
        return
    mkdir(tempFolder)
    for index, expression in enumerate(expressionList):
        print("Info " + sizeLit[index] + " 个随机 " + expression + " 文件开始生成")
        productFiles(index, expression)
        print("Info " + sizeLit[index] + " 个随机 " + expression + " 所有文件已生成")
    if isAvailableTempDict():
        pushAllFiles()
    else:
        print("Error 正则表达式有重复 停止push 请检查config.txt")
    removeTempFolder()
    displayResult()
    print("Complete 执行完成")


main()
