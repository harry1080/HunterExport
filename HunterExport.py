#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# @Author   : Cr4y0n
# @Software : PyCharm
# @Time     : 2021/07/09
# @Github   : https://github.com/Cr4y0nXX

import os
import csv
import time
import datetime
import requests
import configparser
from dateutil.relativedelta import relativedelta

requests.packages.urllib3.disable_warnings()

def printLogo():
    logo = """
           __ __          __          ____                    __ 
          / // /_ _____  / /____ ____/ __/_ __ ___  ___  ____/ /_
         / _  / // / _ \/ __/ -_) __/ _/ \ \ // _ \/ _ \/ __/ __/
        /_//_/\_,_/_//_/\__/\__/_/ /___//_\_\/ .__/\___/_/  \__/ 
                                            /_/           Author：Cr4y0n                 
"""
    msg = """全球鹰Hunter数据导出，仅支持QAX员工接入内网时使用
        
    Usage: python3 HunterExport.py
        Command> app="***"
        
    注：首先接入公司内网，登录安服武器库全球鹰Hunter获取用户名（邮箱）和密钥（Key），写入default.conf配置文件，运行 HunterEcport.py 输入查询指令即可获取数据，并输出至文件。由于全球鹰目前仅在内网开放，因此需要全程接入内网环境。

"""
    print("\033[91m" + logo + "\033[0m")
    print(msg)

# 加载配置
def loadConfFile(fileName):
    try:
        conf = configparser.ConfigParser()
        conf.read(fileName)
        mail = conf.get("Setting", "mail")
        key = conf.get("Setting", "key")
        countMax = conf.getint("Setting", "countMax")
        searchMonth = conf.getint("Setting", "searchMonth")
        return mail, key, countMax, searchMonth
    except:
        print("""\033[31mkey.conf Error, for Example: 
        mail = example@qianxin.com
        key = abcdefgh12345678987654321hgfedcba
        count = 1000
        searchMonth = 6\033[0m\n""")
        exit(0)

# 查询数据
def searchData(mail, key, command, countMax, searchMonth):
    resultList = []
    date = time.strftime("%H:%M:%S", time.localtime())
    print(f"\033[34m[{date}]\033[0m \033[36m[Search]\033[0m  {command}")
    endTime = datetime.date.today()
    startTime = datetime.date.today() - relativedelta(months = +searchMonth)
    url = f'https://geagle.qianxin-inc.cn/openApi/search?username={mail}&api-key={key}&search={command}&start_time={startTime}&end_time={endTime}&page=1&page_size=10&is_web=1'
    rep = requests.get(url, verify=False)
    if rep.json()["code"] == 200:
        repCode, dataTotal, timeSpend = rep.json()["code"], rep.json()["data"]["total"], rep.json()["data"]["time"]
        date = time.strftime("%H:%M:%S", time.localtime())
        print(f"\033[34m[{date}]\033[0m \033[36m[Result]\033[0m  Code: {repCode}   Total: {dataTotal}条   Time: {timeSpend / 1000}秒")
        dataTotal = int(dataTotal)
        if dataTotal > 0:
            nameList = list(rep.json()["data"]["arr"][0].keys())
            if countMax >= dataTotal:
                exportTotal = dataTotal
                pageEnd = int(dataTotal / 100) + 1
            else:
                exportTotal = countMax
                pageEnd = int(countMax / 100) + 1
            date = time.strftime("%H:%M:%S", time.localtime())
            print(
                f"\033[34m[{date}]\033[0m \033[36m[Export]\033[0m  Exporting: {exportTotal}条   ExportMax: {countMax}条   ExportTime: {searchMonth}个月")
            date = time.strftime("%H:%M:%S", time.localtime())
            print(f"\033[34m[{date}]\033[0m \033[36m[Statue]\033[0m  Exporting, Please Waiting……")
            for page in range(1, pageEnd + 1):
                url = f'https://geagle.qianxin-inc.cn/openApi/search?username={mail}&api-key={key}&search={command}&start_time={startTime}&end_time={endTime}&page={page}&page_size=100&is_web=1'
                r = requests.get(url, verify=False)
                dataList = r.json()["data"]["arr"]
                for i in dataList:
                    result = list(i.values())
                    resultList.append(result)
            output(nameList, resultList)
    else:
        date = time.strftime("%H:%M:%S", time.localtime())
        print(f"\033[34m[{date}]\033[0m \033[31m[Error]\033[0m   {rep.json()}")
        # print(rep.json())

# 输出结果
def output(nameList, resultList):
    errorSign = ["\\", "/", ":", "?", "<", ">", "|", "*"]
    date = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    if not os.path.isdir("./output"):
        os.mkdir("./output")
    fileaName = f"{command}_{date}.csv"
    for sign in errorSign:
        if sign in fileaName:
            fileaName = fileaName.replace(sign, "-")
    outputFile = f"./output/{fileaName}".replace("\"", "")
    with open(outputFile, "a", encoding="GB18030", newline="") as f:
        csvWrite = csv.writer(f)
        csvWrite.writerow(nameList)
        for result in resultList:
            csvWrite.writerow(result)
    date = time.strftime("%H:%M:%S", time.localtime())
    print(f"\033[34m[{date}]\033[0m \033[36m[Output]\033[0m  {outputFile}")

if __name__ == "__main__":
    printLogo()
    mail, key, countMax, searchMonth = loadConfFile("./default.conf")
    while True:
        try:
            command = input("\033[31mCommand> \033[0m")
            searchData(mail, key, command, countMax, searchMonth)
        except KeyboardInterrupt:
            print("\nBye~")
            exit(0)
