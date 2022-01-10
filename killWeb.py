#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author:kronoszhang
# @Email:chenzhang1@whu.edu.cn
# @Project: MyCloud
# @File: killWeb.py
# @Datetime:2021/12/27 10:17
# @Software: PyCharm
# -*- coding: UTF-8 -*-
import os
import argparse


def kill_process(port=1224):
    ret = os.popen("netstat -nao|findstr " + str(port))
    processesInfo = ret.read()

    processesListInfo = processesInfo.split("\n")
    try:
        for processInfo in processesListInfo:
            pid = int(processInfo.split("     ")[-1])
            os.popen('taskkill /pid ' + str(pid) + ' /F')
            print("占用端口{}的进程pid={}已被释放！".format(port, pid))
    except Exception:
        print("端口{}目前未被占用！".format(port))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=1224, help="The port will be turned off!")
    args = parser.parse_args()
    kill_process(args.port)
    # output = os.popen('ipconfig')
