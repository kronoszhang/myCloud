#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author:kronoszhang
# @Email:chenzhang1@whu.edu.cn
# @Project: MyCloud
# @File: MyCloud.py
# @Datetime:2021/12/23 14:39
# @Software: PyCharm
import remi.gui as gui
from remi import start, App
import os
import shutil
import base64
import cv2


class MyCloudApp(App):
    def __init__(self, *args):
        super(MyCloudApp, self).__init__(*args)

    def main(self):
        # the margin 0px auto centers the main container
        verticalContainer = gui.Container(width=400, margin='0px auto', style={'display': 'block', 'overflow': 'hidden'})

        horizontalContainer = gui.Container(width='100%', layout_orientation=gui.Container.LAYOUT_HORIZONTAL, margin='0px',
                                            style={'display': 'block', 'overflow': 'auto'})

        subContainerLeft = gui.Container(width=200, style={'display': 'block', 'overflow': 'auto', 'text-align': 'center'})
        self.img = gui.Image(gui.load_resource(r"./webRes/res/logo3.jpg"), weight=200, height=200, margin='10px')
        # the arguments are	width - height - layoutOrientationOrizontal
        subContainerRight = gui.Container(style={'width': '200px', 'display': 'block', 'overflow': 'auto', 'text-align': 'center'})
        self.lbl = gui.Label('', width=200, height=60, margin='10px')

        self.btClassification = gui.Button('资源分类', width=200, height=30, margin='10px')
        self.btDownload = gui.Button('下载资源', width=200, height=30, margin='10px')
        self.btBrowse = gui.Button('浏览资源', width=200, height=30, margin='10px')
        self.btPreview = gui.Button('预览资源', width=200, height=30, margin='10px')
        self.btDeleteClassification = gui.Button('移除分类', width=200, height=30, margin='10px')
        self.btClear = gui.Button('清除', width=200, height=30, margin='10px')
        # setting the listener for the onclick event of the button
        self.btClassification.onclick.do(self.on_buttonClassification_pressed)
        self.btDownload.onclick.do(self.on_buttonDownload_pressed)
        self.btBrowse.onclick.do(self.on_buttonBrowse_pressed)
        self.btPreview.onclick.do(self.on_buttonPreview_pressed)
        self.btClear.onclick.do(self.on_buttonClear_pressed)
        self.btDeleteClassification.onclick.do(self.on_buttonDeleteClassification_pressed)
        self.uploadFilePath = r"./webRes/myCloudBackup"
        if not os.path.exists(self.uploadFilePath):
            os.makedirs(self.uploadFilePath)
        self.resPath = r"./webRes/myCloud"
        if not os.path.exists(self.resPath):
            os.makedirs(self.resPath)
        self.btUploadFile = gui.FileUploader(self.uploadFilePath, multiple_selection_allowed=False, width=200, height=30, margin='10px')
        self.btUploadFile.onsuccess.do(self.fileupload_on_success)
        self.btUploadFile.onfailed.do(self.fileupload_on_failed)

        # self.video = gui.Widget(_type='iframe', width=290, height=200, margin='10px')
        # self.video.attributes['src'] = "https://drive.google.com/file/d/0B0J9Lq_MRyn4UFRsblR3UTBZRHc/preview"
        # self.video.attributes['width'] = '100%'
        # self.video.attributes['height'] = '100%'
        # self.video.attributes['controls'] = 'true'
        # self.video.style['border'] = 'none'
        menu = gui.Menu(width='100%', height='30px')
        menubar = gui.MenuBar(width='100%', height='30px')
        menubar.append(menu)

        # appending a widget to another, the first argument is a string key
        subContainerLeft.append([self.img, self.lbl, self.btUploadFile,
                                 self.btClassification, self.btBrowse, self.btPreview, self.btDeleteClassification,
                                 self.btDownload, self.btClear])
        subContainerRight.append([])
        horizontalContainer.append([subContainerLeft, subContainerRight])
        self.subContainerLeft = subContainerLeft
        self.subContainerRight = subContainerRight
        verticalContainer.append([menubar, horizontalContainer])

        # this flag will be used to stop the display_counter Timer
        self.stop_flag = False

        # kick of regular display of counter

        # returning the root widget
        return verticalContainer

    # listener function
    def on_buttonClassification_pressed(self, widget):
        self.clear()
        if self.res_name:
            allClassification = os.listdir(self.resPath)
            self.lbl_warning = gui.Label('请选择资源的分类标签：', width=200, height=30, margin='10px')
            # self.tree = gui.TreeView(width=250, height='100%', margin='10px')
            # for item in allClassification:
            #     item_res = os.listdir(os.path.join(self.resPath, item))
            #     image_num, video_num, total_num = 0, 0, len(item_res)
            #     for _ in item_res:
            #         _ = _.lower()
            #         if _.endswith(".mp4") or _.endswith(".avi"):
            #             video_num += 1
            #         if _.endswith(".jpg") or _.endswith(".png") or _.endswith(".gif") or _.endswith(".jpeg"):
            #             image_num += 1
            #     item_idx = gui.TreeItem("【{}】 资源{}图片{}视频{}".format(item, total_num, image_num, video_num))
            #     self.tree.append([item_idx])
            # self.subContainerLeft.append([self.lbl_warning, self.tree])

            items = list()
            for item in allClassification:
                item_res = os.listdir(os.path.join(self.resPath, item))
                image_num, video_num, total_num = 0, 0, len(item_res)
                for _ in item_res:
                    _ = _.lower()  # _仅用于统计不用于其他复制/浏览等操作,所以整个file小写不影响,否则只能_[-4:]小写
                    if _.endswith(".mp4") or _.endswith(".avi"):
                        video_num += 1
                    if _.endswith(".jpg") or _.endswith(".png") or _.endswith(".gif") or _.endswith(".jpeg"):
                        image_num += 1
                item_info = "【{}】 资源{}图片{}视频{}".format(item, total_num, image_num, video_num)
                items.append(item_info)
            item_info = "【类别标签】不够？点这里~"
            items.append(item_info)
            self.listViewClassification = gui.ListView.new_from_list(items, width=200, height=120, margin='10px')
            self.listViewClassification.onselection.do(self.listViewClassification_on_selected)
            self.subContainerLeft.append(self.lbl_warning, key='lbl_warning')
            self.subContainerLeft.append(self.listViewClassification, key='listViewClassification')

    def listViewClassification_on_selected(self, widget, selected_item_key):
        """ The selection event of the listView, returns a key of the clicked event.
            You can retrieve the item rapidly
        """
        if self.listViewClassification.children[selected_item_key].get_text() != "【类别标签】不够？点这里~":
            # 将【上传的文件】分类到【指定标签下】
            dstClassification = \
                self.listViewClassification.children[selected_item_key].get_text().split("】")[0].split("【")[1]
            shutil.copy(
                os.path.join(self.uploadFilePath, self.res_name),
                os.path.join(self.resPath, dstClassification, self.res_name)
            )
            self.lbl.set_text('资源{}已分类到【{}】标签中！'.format(
                self.res_name,
                dstClassification)
            )
            # 清除【资源分类】标签
            self.subContainerLeft.remove_child(self.subContainerLeft.children['lbl_warning'])
            self.subContainerLeft.remove_child(self.subContainerLeft.children['listViewClassification'])
        else:
            self.inputDialog = gui.InputDialog(
                '类别标签',
                '请输入你想新建的类别标签',
                initial_value='',
                width=400
            )
            self.inputDialog.confirm_value.do(self.on_input_dialog_confirm)
            self.inputDialog.show(self)

    def on_input_dialog_confirm(self, widget, value):
        newClassification = os.path.join(self.resPath, value)
        if not os.path.exists(newClassification):
            os.makedirs(newClassification)
        self.lbl.set_text('类别标签【{}】已建立! '.format(value))
        # 清除【资源分类】标签
        self.subContainerLeft.remove_child(self.subContainerLeft.children['lbl_warning'])
        self.subContainerLeft.remove_child(self.subContainerLeft.children['listViewClassification'])

    def on_buttonDownload_pressed(self, widget):
        self.subContainerDownLoad = gui.Container(
            margin='0px', style={'width': '220px', 'display': 'block', 'overflow': 'auto', 'text-align': 'center'}
        )
        fdownloader = gui.FileDownloader(
            '请点击这里下载资源', os.path.join(self.uploadFilePath, self.res_name), width=200, height=30, margin='0px')
        self.subContainerDownLoad.append(fdownloader, key='file_downloader')
        self.subContainerLeft.append(self.subContainerDownLoad, key="subContainerDownLoad")

    def on_buttonBrowse_pressed(self, widget):
        self.clear()
        # 浏览资源前先清空其他区域
        allClassification = os.listdir(self.resPath)
        items = list()
        for item in allClassification:
            item_res = os.listdir(os.path.join(self.resPath, item))
            image_num, video_num, total_num = 0, 0, len(item_res)
            for _ in item_res:
                _ = _.lower()
                if _.endswith(".mp4") or _.endswith(".avi"):
                    video_num += 1
                if _.endswith(".jpg") or _.endswith(".png") or _.endswith(".gif") or _.endswith(".jpeg"):
                    image_num += 1
            item_info = "【{}】 资源{}图片{}视频{}".format(item, total_num, image_num, video_num)
            items.append(item_info)
        # 总资源库
        allRes = os.listdir(self.uploadFilePath)
        image_num, video_num, total_num = 0, 0, len(allRes)
        for _ in allRes:
            _ = _.lower()
            if _.endswith(".mp4") or _.endswith(".avi"):
                video_num += 1
            if _.endswith(".jpg") or _.endswith(".png") or _.endswith(".gif") or _.endswith(".jpeg"):
                image_num += 1
        item_info = "【总资源库】 资源{}图片{}视频{}".format(total_num, image_num, video_num)
        items.append(item_info)
        self.listViewBrowse = gui.ListView.new_from_list(items, width=200, height=120, margin='10px')
        self.listViewBrowse.onselection.do(self.listViewBrowse_on_selected)
        self.subContainerLeft.append(self.listViewBrowse, key='listViewBrowse')

    def on_buttonPreview_pressed(self, widget):
        self.clear()
        # 浏览资源前先清空其他区域
        allClassification = os.listdir(self.resPath)
        items = list()
        for item in allClassification:
            item_res = os.listdir(os.path.join(self.resPath, item))
            image_num, video_num, total_num = 0, 0, len(item_res)
            for _ in item_res:
                _ = _.lower()
                if _.endswith(".mp4") or _.endswith(".avi"):
                    video_num += 1
                if _.endswith(".jpg") or _.endswith(".png") or _.endswith(".gif") or _.endswith(".jpeg"):
                    image_num += 1
            item_info = "【{}】 资源{}图片{}视频{}".format(item, total_num, image_num, video_num)
            items.append(item_info)
        # 总资源库
        allRes = os.listdir(self.uploadFilePath)
        image_num, video_num, total_num = 0, 0, len(allRes)
        for _ in allRes:
            _ = _.lower()
            if _.endswith(".mp4") or _.endswith(".avi"):
                video_num += 1
            if _.endswith(".jpg") or _.endswith(".png") or _.endswith(".gif") or _.endswith(".jpeg"):
                image_num += 1
        item_info = "【总资源库】 资源{}图片{}视频{}".format(total_num, image_num, video_num)
        items.append(item_info)
        self.lbl.set_text("预览模式只能快速浏览文件,需要下载资源或修改图像分类请使用【浏览资源】~")
        self.listViewPreview = gui.ListView.new_from_list(items, width=200, height=120, margin='10px')
        self.listViewPreview.onselection.do(self.listViewPreview_on_selected)
        self.subContainerLeft.append(self.listViewPreview, key='listViewPreview')

    def on_buttonDeleteClassification_pressed(self, widget):
        self.clear()
        if self.dstBrowse != "总资源库":
            filePath = os.path.join(self.resPath, self.dstBrowse)
            files = os.listdir(filePath)
            # 选中的要删除的图片转base64
            with open(os.path.join(self.uploadFilePath, self.res_name), "rb") as f:  # 转为二进制格式
                toDeletedImageBase64Data = base64.b64encode(f.read())  # 使用base64进行加密
            for file in files:
                # image转base64
                with open(os.path.join(filePath, file), "rb") as f:
                    base64_data = base64.b64encode(f.read())
                if base64_data == toDeletedImageBase64Data:
                    break
            # 将文件从分类里面移除
            os.remove(os.path.join(filePath, file))
        else:
            self.lbl.set_text("不能删除总资源库的内容哦~")

    def listViewBrowse_on_selected(self, widget, selected_item_key):
        """ The selection event of the listView, returns a key of the clicked event.
            You can retrieve the item rapidly
        """
        # 浏览模式下加载的是原图, 用户可以对图像进行浏览、下载、分类(给图像打标签)、移除分类(修改图像标签)操作,可以理解为【操作资源】而不是仅仅【预览资源】
        # 这个过程由于网页会加载原图,因此会很慢,所以最好是上传资源的时候就进行分类,而下载操作其实一般用不上

        # 将【上传的文件】分类到【指定标签下】
        self.dstBrowse = self.listViewBrowse.children[selected_item_key].get_text().split("】")[0].split("【")[1]
        self.lbl.set_text('正在浏览类别标签【{}】下的资源...'.format(self.dstBrowse))
        # 清除【资源分类】标签
        self.subContainerLeft.remove_child(self.subContainerLeft.children['listViewBrowse'])
        # 浏览资源
        filePath = os.path.join(self.resPath, self.dstBrowse)
        if self.dstBrowse == "总资源库":
            filePath = self.uploadFilePath
        for file in os.listdir(filePath):
            if file[-4:].lower().endswith(".jpg") or file[-4:].lower().endswith(".png") or \
                    file[-5:].lower().endswith(".jpeg"):
                self.img_file = gui.Image(gui.load_resource(os.path.join(filePath, file)), height=50, margin='5px')
                self.preview = False
                self.img_file.onclick.do(self.on_img_clicked)
                self.subContainerRight.append([self.img_file])

    def listViewPreview_on_selected(self, widget, selected_item_key):
        """ The selection event of the listView, returns a key of the clicked event.
            You can retrieve the item rapidly
        """
        # 预览模式下是用于快速浏览图像,不能操作图像

        # 将【上传的文件】分类到【指定标签下】
        self.dstPreview = self.listViewPreview.children[selected_item_key].get_text().split("】")[0].split("【")[1]
        self.lbl.set_text('正在预览类别标签【{}】下的资源...'.format(self.dstPreview))
        # 清除【资源分类】标签
        self.subContainerLeft.remove_child(self.subContainerLeft.children['listViewPreview'])
        # 浏览资源
        filePath = os.path.join(self.resPath, self.dstPreview)
        if self.dstPreview == "总资源库":
            filePath = self.uploadFilePath
        # 临时文件夹
        tempPath = r"./webRes/temp"
        if os.path.exists(tempPath):
            shutil.rmtree(tempPath)
        os.makedirs(tempPath)
        for file in os.listdir(filePath):
            if file[-4:].lower().endswith(".jpg") or file[-4:].lower().endswith(".png") or \
                    file[-5:].lower().endswith(".jpeg"):
                # 将需要预览的图像缩小size另存到tempPath文件中,避免gui.Image加载较大的原图出现很慢的问题
                img = cv2.imread(os.path.join(filePath, file))
                self.imgH, self.imgW, imgC = img.shape
                img = cv2.resize(img, (200, int(200 * self.imgH / self.imgW)), interpolation=cv2.INTER_LINEAR)
                cv2.imwrite(os.path.join(tempPath, file), img)
                # 加载比较小的预览图,而不是预览图,避免漫长的等待过程
                self.img_file = gui.Image(gui.load_resource(os.path.join(tempPath, file)), height=50, margin='5px')
                self.preview = True
                self.img_file.onclick.do(self.on_img_clicked)
                self.subContainerRight.append([self.img_file])


    def on_img_clicked(self, widget):
        if not self.preview:
            self.lbl.set_text('资源可保存或修改分类哦~')
        else:
            self.lbl.set_text('预览模式下资源是低质量结果,请谨慎使用保存或修改分类哦~')
        # img中的base64转图像保存到本地
        self.imgdata = base64.b64decode(self.img_file.attr_src.split("base64,")[1])
        self.res_name = "{:06d}.png".format(len(os.listdir(self.uploadFilePath)))
        file = open(os.path.join(self.uploadFilePath, self.res_name), 'wb')
        file.write(self.imgdata)
        if self.preview:
            # 预览模式下还是可以支持下载【预览的低质量图像的】,但其实没啥用
            # 将需要预览的图像缩小size另存到tempPath文件中,避免gui.Image加载较大的原图出现很慢的问题
            img = cv2.imread(os.path.join(self.uploadFilePath, self.res_name))
            img = cv2.resize(img, (self.imgH, self.imgW), interpolation=cv2.INTER_LINEAR)
            cv2.imwrite(os.path.join(self.uploadFilePath, self.res_name), img)
        file.close()

    def on_buttonClear_pressed(self, widget):
        self.clear()

    def clear(self):
        self.lbl.set_text("")  # 清空label的内容
        self.subContainerRight.empty()
        try:
            self.subContainerDownLoad.empty()
            self.subContainerLeft.remove_child(self.subContainerLeft.children['subContainerDownLoad'])
        except:
            pass
        try:
            self.subContainerLeft.remove_child(self.subContainerLeft.children['lbl_warning'])
            self.subContainerLeft.remove_child(self.subContainerLeft.children['listViewClassification'])
        except:
            pass
        try:
            self.subContainerLeft.remove_child(self.subContainerLeft.children['listViewBrowse'])
        except:
            pass

    def fileupload_on_success(self, widget, filename):
        # filename = "{:06d}".format(len(os.listdir(self.uploadFilePath)) + 1) + filename[-4:]  # 文件重命名
        self.res_name = filename
        self.lbl.set_text('{}文件上传成功！'.format(filename))

    def fileupload_on_failed(self, widget, filename):
        self.lbl.set_text('{}文件上传失败！'.format(filename))

    def on_close(self):
        """ Overloading App.on_close event to stop the Timer.
        """
        self.stop_flag = True
        super(MyCloudApp, self).on_close()


if __name__ == "__main__":
    myIP = '0.0.0.0'  # 可以换成你的内网IP,然后所有连接到这个IP网络的设备就都可以访问这个网址了; 但如果设置外网IP会启动失败,why?
    port = 1224
    start(
        MyCloudApp,
        address=myIP,
        port=port,
        multiple_instance=True,
        enable_file_cache=True,
        update_interval=0.1,
        start_browser=True,
        standalone=False,
        debug=True,
        # username='ChronousZ',
        # password='ChronousZ',
    )
