#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author:kronoszhang
# @Email:chenzhang1@whu.edu.cn
# @Project: actiontransclinet
# @File: demo.py
# @Datetime:2021/12/23 14:39
# @Software: PyCharm
import os

import remi.gui as gui
from remi import start, App
import tkinter
from ssh import fileTransfer
import shutil
from zip import writeAllFileToZip
import zipfile
import sys
from threading import Timer
from getDeviceInfo import getMemCpuGPU
sys.path.insert(0, r"D:\Users\Desktop\frankmocap")


# 重要参数配置
localRelease = True  # 本地发布还是公开发布
localIP = '127.0.0.1'  # web服务器的本地IP
port = 1224  # web服务器端口
thisComputerIP = '10.15.164.77'  # web服务器的实际IP


class ChronousZApp(App):
    def __init__(self, *args):
        super(ChronousZApp, self).__init__(*args)

    def idle(self):
        freeMemory, totalMemory, CPUPercent, freeGPUMemory, totalGPUMemory = getMemCpuGPU()
        self.lbl_dev.set_text(
            '--------------------------------------------------'
            '服务器CPU使用率: {:0.2f}% 服务器内存剩余: {:0.2f}G/{:0.2f}G 服务器显存剩余: {:0.2f}G/{:0.2f}G '
            '注意: 显存低于4G时请勿开始处理! '
            '--------------------------------------------------'.format(
                CPUPercent, freeMemory, totalMemory, freeGPUMemory, totalGPUMemory))

    def main(self):
        screen = tkinter.Tk()
        # 获取当前屏幕的宽和高
        width, height = screen.winfo_screenwidth(), screen.winfo_screenheight()
        # 容器-用来放组件
        verticalContainer = gui.Container(width=width, height=height, margin='0px auto', style={'display': 'block', 'overflow': 'hidden'})
        horizontalContainer = gui.Container(width='100%', layout_orientation=gui.Container.LAYOUT_HORIZONTAL, margin='0px',
                                            style={'display': 'block', 'overflow': 'auto'})
        subContainerLeft = gui.Container(width=320, style={'display': 'block', 'overflow': 'auto', 'text-align': 'center'})
        subContainerRight = gui.Container(style={'width': '1600px', 'display': 'block', 'overflow': 'auto', 'text-align': 'justify'})
        subContainerDownLoad = gui.Container(margin='50px',
                                             style={'width': '220px', 'display': 'block', 'overflow': 'auto', 'text-align': 'center'})

        # 组件
        self.img = gui.Image(gui.load_resource(r"./webRes/res/logo2.png"), height=50, weight=100, margin='20px')
        # self.img = gui.Image('/res:logo.png', height=100, margin='10px')
        self.lblWarning = gui.Label(
            "使用说明：1. [可选]先上传参数,需按照模板填写; 2. 选择要处理的视频并点击上传; 3. 点击开始处理; 4. 下载动捕文件bvh和fbx; "
            "5.注意: 这是私人IP,没有任何防护措施,请勿随意发送网址！谢谢~",
            width=200, height=100, margin='50px', style={'text-align': 'left'})
        self.lbl_dev = gui.Label('', width=200, height=100, margin='50px')
        self.lbl = gui.Label('', width=200, height=30, margin='50px', style={'text-align': 'center'})
        uploadFilePath = r"./webRes/res/tempFiles"
        if not os.path.exists(uploadFilePath):
            os.makedirs(uploadFilePath)
        self.btUploadFile = gui.FileUploader(uploadFilePath, width=200, height=30, margin='10px')
        self.btUploadFile.onsuccess.do(self.fileupload_on_success)
        self.btUploadFile.onfailed.do(self.fileupload_on_failed)
        self.btUploadVideo = gui.Button('上传视频', width=200, height=30, margin='10px')
        self.btUploadVideo.onclick.do(self.on_buttonUploadVideo_pressed)
        self.btUploadParam = gui.Button('上传参数', width=200, height=30, margin='10px')
        self.btUploadParam.onclick.do(self.on_buttonUploadParam_pressed)
        self.btStart = gui.Button('开始处理', width=200, height=30, margin='10px')
        self.btStart.onclick.do(self.on_buttonStart_pressed)
        self.btDownloadBVH = gui.Button('下载动捕结果', width=200, height=30, margin='10px')
        self.btDownloadBVH.onclick.do(self.on_buttonDownloadBVH_pressed)
        self.btClear = gui.Button('清除下载链接', width=200, height=30, margin='10px')
        # self.btClear = gui.Button('清除下载链接', width=200, height=30, margin='10px', style={'visibility': 'hidden'})
        self.btClear.onclick.do(self.on_buttonClear_pressed)
        if localRelease:
            self.btClearTemp = gui.Button('清除本地文件', width=200, height=30, margin='10px')
            self.btClearTemp.onclick.do(self.on_buttonClearTemp_pressed)
        self.btBrowse = gui.Button('浏览', width=200, height=30, margin='10px')
        self.btBrowse.onclick.do(self.on_buttonBrowse_pressed)

        # appending a widget to another, the first argument is a string key
        subContainerDownLoad.append([])
        subContainerLeft.append(
            [
                self.img,
                self.lblWarning,
                self.lbl_dev,
                self.lbl,
                self.btUploadFile,
                self.btUploadVideo,
                self.btUploadParam,
                self.btStart,
                self.btDownloadBVH,
                self.btClear,
                self.btBrowse,
            ]
        )
        if localRelease:
            subContainerLeft.append([self.btClearTemp])
        subContainerLeft.append([subContainerDownLoad])

        subContainerRight.append([])
        self.subContainerLeft = subContainerLeft
        self.subContainerRight = subContainerRight
        self.subContainerDownLoad = subContainerDownLoad
        horizontalContainer.append([subContainerLeft, subContainerRight])

        menu = gui.Menu(width='100%', height='30px')
        menubar = gui.MenuBar(width='100%', height='30px')
        menubar.append(menu)
        verticalContainer.append([menubar, horizontalContainer])

        # this flag will be used to stop the display_device Timer
        self.stop_flag = False

        # kick of regular display of device
        self.display_device()

        # returning the root widget
        return verticalContainer

    # listener function
    def on_buttonUploadParam_pressed(self, widget):
        """
        上传参数配表
        """
        self.lbl.set_text("请上传你的参数...[参数配置功能暂未实现]")
        # TODO 上传指定名字的参数表
        self.video = 'cxk1s.mp4'
        self.renderImageDisplay()
        pass

    def on_buttonStart_pressed(self, widget):
        """
        执行动捕算法
        """
        # 写可执行文件,用于后续执行动捕检测
        with open("winRun.sh", "w") as f:
            f.write(r"cd 'D:\Users\Desktop\frankmocap'" + "\n")
            f.write(r"source activate frankmocap" + "\n")  # 激活frankmocap的anaconda虚拟环境
            f.write(
                r"python -m demo.demo_frankmocap --input_path 'D:\Users\Desktop\actiontransclinet\webRes\inputVideo\{}' "
                r"--out_dir 'D:\Users\Desktop\actiontransclinet\webRes\outputMocap'  --reload "
                r"> 'D:\Users\Desktop\actiontransclinet\webRes\outputMocap\{}\runResults.txt'".format(
                    self.video, self.video[:-4]) + "\n")  # 执行动作捕捉

        # TODO self.lbl只能显示一个`处理完成`
        self.lbl.set_text('正在处理中，请稍后...')  # 显示不出来
        runFlag = os.system(r'winRun.sh')
        if not runFlag:
            # 返回结果为0则表示上面os.system执行成功
            self.lbl.set_text('处理完成!')
            # 调用渲染展示接口
            self.renderImageDisplay()

    def on_buttonDownloadBVH_pressed(self, widget):
        """
        下载动捕文件
        """
        if self.video.split(".")[1].lower() in ['mp4', 'avi']:
            # 压缩bvh和fbx动捕文件(美术),以及pkl文件(算法)
            outputMocapPathTemp = r"./webRes/outputMocap/{}_Mocap".format(self.video[:-4])
            outputMocapPath = r"./webRes/outputMocap/{}".format(self.video[:-4])
            if not os.path.exists(outputMocapPathTemp):
                os.makedirs(outputMocapPathTemp)
            for file in os.listdir(outputMocapPath):
                if ('.bvh' in file) or ('.fbx' in file):
                    shutil.copy(os.path.join(outputMocapPath, file), os.path.join(outputMocapPathTemp, file))
                if file == 'mocap':
                    if not os.path.exists(os.path.join(outputMocapPathTemp, 'mocap')):
                        os.makedirs(os.path.join(outputMocapPathTemp, 'mocap'))
                    for pklFile in os.listdir(os.path.join(outputMocapPath, 'mocap')):
                        shutil.copy(os.path.join(outputMocapPath, 'mocap', pklFile), os.path.join(outputMocapPathTemp, 'mocap', pklFile))
            zipFilePath = os.path.join(r"./webRes/outputMocap", "{}_Mocap.zip".format(self.video[:-4]))
            zipFile = zipfile.ZipFile(zipFilePath, "w", zipfile.ZIP_DEFLATED)
            writeAllFileToZip(outputMocapPathTemp, zipFile)  # 开始压缩
            # 生成下载链接
            self.fdownloader = gui.FileDownloader('请点击此处下载动捕结果', zipFilePath, width=200, height=30, margin='10px')
            self.subContainerDownLoad.append(self.fdownloader, key='file_downloader')  # key可以避免弹出很多个链接

    def on_buttonClear_pressed(self, widget):
        """
        清除下载链接
        """
        # self.subContainerDownLoad.remove_child(self.subContainerDownLoad.children['file_downloader'])
        self.subContainerDownLoad.empty()

    def on_buttonBrowse_pressed(self, widget):
        """
        浏览指定视频
        """
        # 上传视频后点击这个按钮就可以浏览对应视频的渲染图了(选择视频即可,不用上传)
        self.renderImageDisplay()

    def on_buttonClearTemp_pressed(self, widget):
        """
        清楚本地文件
        """
        os.remove(r"./winRun.sh")
        shutil.rmtree(r"./webRes/inputVideo")
        shutil.rmtree(r"./webRes/outputMocap")
        shutil.rmtree(r"./webRes/res/tempFiles")
        self.lbl.set_text('已全部清除!')

    def on_buttonUploadVideo_pressed(self, widget):
        """
        上传要处理的视频
        1. 视频会先上传到本项目的web服务器的res/tempFiles目录下,然后上传到远程linux存储服务器,然后在下载到frankmocap所在的运算服务器来执行动捕,这样能保证最高效
           (web服务器需要稳定,运算服务器需要算力,两者的输入输出都应被及时清理,但中间存储服务器需要大容量来保存所有结果而不清理)
        2. 由于本机的web服务器和frankmocap的运算服务器其实是一台机器,而linux存储服务器也是虚拟的,所以其实可以跳过中间linux过程,直接将上传到res/tempFiles的文件
           复制到inputVideo中
        """
        useRomoteLinux = False
        if self.video[-3:].lower() in ['mp4', 'avi']:
            # 创建web服务器的数据存储路径
            inputVideoPath, outputMocapPath = r"./webRes/inputVideo", r"./webRes/outputMocap"
            if not os.path.exists(inputVideoPath):
                os.makedirs(inputVideoPath)
            if not os.path.exists(outputMocapPath):
                os.makedirs(outputMocapPath)
            if not os.path.exists(os.path.join(outputMocapPath, "{}".format(self.video[:-4]))):
                os.makedirs(os.path.join(outputMocapPath, "{}".format(self.video[:-4])))

            if useRomoteLinux:
                # 将用户选择的视频文件上传到中转的linux服务器
                self.lbl.set_text('正在上传视频, 请稍后...')
                fileTransfer(r"./webRes/res/tempFiles/{}".format(self.video), r"/data/frankmocap_data/input/", direction='put')
                self.lbl.set_text('{} 上传成功！'.format(self.video))
                # 从linux中转服务器中将文件取到frankmocap项目的服务器的位置
                fileTransfer(inputVideoPath, r"/data/frankmocap_data/input/{}".format(self.video), direction='get')
            else:
                # 直接从web服务器复制到frankmocap算力服务器
                self.lbl.set_text('正在上传视频, 请稍后...')
                shutil.copy(r"./webRes/res/tempFiles/{}".format(self.video), r"{}/{}".format(inputVideoPath, self.video))
                self.lbl.set_text('{} 上传成功！'.format(self.video))
        else:
            self.lbl.set_text('{} 不是视频文件！'.format(self.video))

    def on_buttonLastFrame_pressed(self, widget):
        self.curFrameNums -= 1
        if self.curFrameNums < 0:
            self.curFrameNums = 0
        self.lbl_Frame.set_text("{} / {}".format(self.curFrameNums, self.totalFrameNums))
        self.imgRender.set_image(gui.load_resource(r"./webRes/outputMocap/{}/rendered/{:05}.jpg".format(self.video[:-4], self.curFrameNums)))

    def on_buttonNextFrame_pressed(self, widget):
        self.curFrameNums += 1
        if self.curFrameNums > self.totalFrameNums:
            self.curFrameNums = self.totalFrameNums
        self.lbl_Frame.set_text("{} / {}".format(self.curFrameNums, self.totalFrameNums))
        self.imgRender.set_image(gui.load_resource(r"./webRes/outputMocap/{}/rendered/{:05}.jpg".format(self.video[:-4], self.curFrameNums)))

    def on_buttonClose_pressed(self, widget):
        self.subContainerRight.empty()

    def renderImageDisplay(self):
        self.imgRender = gui.Image(gui.load_resource(r"./webRes/outputMocap/{}/rendered/00000.jpg".format(self.video[:-4])),
                                   weight=1280, height=360, margin='10px')  # 16:9 但render图像宽度*2了
        self.curFrameNums, self.totalFrameNums = 0, len(os.listdir(r"./webRes/outputMocap/{}/rendered".format(self.video[:-4]))) - 1
        self.lbl_Frame = gui.Label(' 0 / {}'.format(self.totalFrameNums),
                                   width=50, height=20, margin='10px', style={'text-align': 'center'})
        self.btLastFrame = gui.Button('上一帧', width=100, height=30, margin='10px')
        # self.btLastFrame = gui.Button('上一帧', width=100, height=30, margin='10px', style={'visibility': 'hidden'})
        self.btLastFrame.onclick.do(self.on_buttonLastFrame_pressed)
        self.btNextFrame = gui.Button('下一帧', width=100, height=30, margin='10px')
        self.btNextFrame.onclick.do(self.on_buttonNextFrame_pressed)
        self.btClose = gui.Button('关闭', width=100, height=30, margin='10px')
        self.btClose.onclick.do(self.on_buttonClose_pressed)
        self.frameIdxSpinBox = gui.SpinBox(min=0, max=self.totalFrameNums, margin='10px',
                                           width=100, height=30, style={'text-align': 'center', 'border-style': 'none'})
        self.frameIdxSpinBox.set_value('0')
        self.btJump = gui.Button('跳转', width=100, height=30, margin='10px')
        self.btJump.onclick.do(self.on_buttonJump_pressed)
        self.subContainerRight.append([self.imgRender, self.lbl_Frame, self.btLastFrame, self.btNextFrame, self.btClose,
                                       self.frameIdxSpinBox, self.btJump])

    def on_buttonJump_pressed(self, widget):
        self.curFrameNums = int(self.frameIdxSpinBox.get_value())
        if (self.curFrameNums > self.totalFrameNums) or (self.curFrameNums < 0):
            return
        self.lbl_Frame.set_text("{} / {}".format(self.curFrameNums, self.totalFrameNums))
        self.imgRender.set_image(
            gui.load_resource(r"./webRes/outputMocap/{}/rendered/{:05}.jpg".format(self.video[:-4], self.curFrameNums)))

    def fileupload_on_success(self, widget, filename):
        self.video = filename

    def fileupload_on_failed(self, widget, filename):
        self.lbl.set_text('视频上传失败,请重试...')

    def display_device(self):
        if not self.stop_flag:
            Timer(1, self.display_device).start()  # 每隔1s刷新一次

    def on_close(self):
        """ Overloading App.on_close event to stop the Timer.
        """
        self.stop_flag = True
        super(ChronousZApp, self).on_close()


if __name__ == "__main__":
    # starts the webserver
    if localRelease:
        # 1. 发布为仅本地可用的私密网站
        start(
            ChronousZApp,
            address=localIP,
            port=port,
            multiple_instance=True,  # 如果为True，连接到你脚本的多个客户端会有不同的应用情况（由唯一的cookie会话标识符标识）
            enable_file_cache=True,  # 如果为True，会使资源缓存
            update_interval=0.1,  # 以秒为单位的GUI更新间隔. 如果是0, 则每个更改会伴随一次更新且App.idle方式无法被调用.
            start_browser=True,  # 定义浏览器是否应该在启动时自动打开
            standalone=False,  # 指明了在何处运行应用程序.如果为True,则以标准窗口模式运行.如果为False，则界面显示在浏览器网页中.
            debug=True,
            # 额外参数(AdditionalParameters):
            # username: 为了基本的HTTP认证(输入username和password的才能访问网站)
            # password: 为了基本的HTTP认证
            # certfile: SSL证书文件名
            # keyfile: SSL密匙文件
            # ssl_version: 认证版本(i.e.ssl.PROTOCOL_TLSv1_2).如果禁用SSL加密.
        )
    else:
        # 2. 发布为“有网址就可以调用的”版本
        start(
            ChronousZApp,
            address=thisComputerIP,
            port=port,
            multiple_instance=True,
            enable_file_cache=True,
            update_interval=0.1,
            start_browser=True,
            standalone=False,
            debug=True,
            username='ChronousZ',
            password='ChronousZ',
        )
