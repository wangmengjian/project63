# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ros_iop_ocu.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import time,datetime
from  iopConnection.IopSystem import IopSystem
import pointCloudShow
import cv2


import rospy
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
import sys
import subprocess

from geometry_msgs.msg import Twist, Point, Quaternion
import geometry_msgs.msg
import threading
import numpy as np
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge, CvBridgeError
import cv2

reload(sys)
sys.setdefaultencoding('utf8')

class Ui_MainWindow(object):

    def __init__(self,MainWindow):
        self.mWin=MainWindow

        #set backgrround color
        self.green = "QPushButton{background-color:green}"
        self.gray = "QPushButton{background-color:none}"
        self.configInfo={"CPUArch":"amd64","Name":"waffle1","Payload":{"相机":"双目相机","雷达":"十六线激光雷达","机械臂":"AUBO"},"ROSversion":"kinetic","System":"Raspbian"}
        self.cam0_path = '/home/ym/cam0/'  # 已经建立好的存储cam0 文件的目录
        self.cam1_path = '/home/ymt/cam1/'
        self.bridge = CvBridge()
        self.robotlist=[]
        #将选择的设备和他的属性加入到这个列表中
        self.selectedRobotlist={}



        self.setupUi(self.mWin)
        # self.cmdThread = QTProcessThread()
        # self.cmdThread.updateSig.connect(self.upDateMessage)
        # self.cmdThread.start()
        # time.sleep(1)
        self.init_ros()
        # time.sleep(1)

        self.iopsys = IopSystem()
        # 线速度
        self.linearspeed =round(3.5*self.linearverticalSlider.value()/self.linearverticalSlider.maximum(),1)
        #角速度
        self.angularspeed = round(1.5*self.angularverticalSlider.value()/self.angularverticalSlider.maximum(),1)
        self.otherWidget()


        # print "self.iopsys.robotList",self.iopsys.robotList

        time.sleep(1)
        self.refresh_iop_system_thread()
        self.refresh()
        self.platform_server(self.robotlist)
        self.setEvent()
        self.setFlag()
        self.auboshowImageLabel()
        # self.showConfigInfo()
        self.platform_flag = True

        self.multilinearspeed = round(3.5 * self.linearmultirobotverticalSlider.value() / self.linearmultirobotverticalSlider.maximum(), 1)
        # 角速度
        self.multiangularspeed = round(1.5 * self.angularmultirobotverticalSlider.value() / self.angularmultirobotverticalSlider.maximum(),1)

        # self.showServiceList("turtlebot3_burger1")

    #　刷新服务线程
    def refresh_iop_system_thread(self):
        print "hjujdsgvedshjvgioesdjvkldfsiofvjdfiosx"
        t1=threading.Thread(target=self.refresh_iop_system)
        t1.start()
    def refresh_iop_system(self):
        self.old_robotlist=self.robotlist
        while True:
            self.robotlist=self.iopsys.showRobotList()
            if self.old_robotlist!=self.robotlist:
                self.platform_server(self.robotlist)
            self.old_robotlist=self.robotlist
            print 'refresh'
            time.sleep(3)

    def setEvent(self):
        self.robotlistTreeWidget.clicked.connect(self.robotClickedFun)
        print "event starting "
        self.tabWidget.currentChanged['int'].connect(self.tabfun)

        self.okButton.clicked.connect(self.agentCon)
        self.cancelcontrolButton.clicked.connect(self.cancelCon)
        self.frontButton.pressed.connect(lambda :self.tansEvent(self.frontButton.text()))
        self.backButton.pressed.connect(lambda :self.tansEvent(self.backButton.text()))
        self.leftButton.pressed.connect(lambda :self.tansEvent(self.leftButton.text()))
        self.rightButton.pressed.connect(lambda :self.tansEvent(self.rightButton.text()))

        self.frontButton.released.connect(lambda: self.button_releaseed(self.frontButton.text()))
        self.backButton.released.connect(lambda: self.button_releaseed(self.backButton.text()))
        self.leftButton.released.connect(lambda: self.button_releaseed(self.leftButton.text()))
        self.rightButton.released.connect(lambda: self.button_releaseed(self.rightButton.text()))

        #进度条改变事件
        self.linearverticalSlider.valueChanged.connect(self.changedLinear_angular)
        self.angularverticalSlider.valueChanged.connect(self.changedLinear_angular)

        self.linearmultirobotverticalSlider.valueChanged.connect(self.changedMultiLinear_angular)
        self.angularmultirobotverticalSlider.valueChanged.connect(self.changedMultiLinear_angular)

        self.linearplusButton.clicked.connect(lambda :self.addverticalSlider(self.linearverticalSlider))
        self.angularplusButton.clicked.connect(lambda :self.addverticalSlider(self.angularverticalSlider))
        self.linearsubButton.clicked.connect(lambda :self.subverticalSlider(self.linearverticalSlider))
        self.angularsubButton.clicked.connect(lambda :self.subverticalSlider(self.angularverticalSlider))

        # self.frontButton.pressed.connect(self.sss)
        # self.frontButton.released.connect(self.button_released)
        self.frontButton.setAutoRepeat(True)
        self.backButton.setAutoRepeat(True)
        self.rightButton.setAutoRepeat(True)
        self.leftButton.setAutoRepeat(True)

        ###多智能体事件

        self.multirobotokButton.clicked.connect(self.getMultiRobotAcessControl)
        self.multirobotcancelcontrolButton.clicked.connect(self.releaseMultiRobotControl)
        self.frontmultirobotButton.pressed.connect(lambda :self.MultiRobotControl(self.frontmultirobotButton.text()))
        self.backmultirobotButton.pressed.connect(lambda :self.MultiRobotControl(self.backmultirobotButton.text()))
        self.leftmultirobotButton.pressed.connect(lambda :self.MultiRobotControl(self.leftmultirobotButton.text()))
        self.rightmultirobotButton.pressed.connect(lambda :self.MultiRobotControl(self.rightmultirobotButton.text()))

        self.frontmultirobotButton.released.connect(lambda: self.MultiRobotControl_released(self.frontmultirobotButton.text()))
        self.backmultirobotButton.released.connect(lambda: self.MultiRobotControl_released(self.backmultirobotButton.text()))
        self.leftmultirobotButton.released.connect(lambda: self.MultiRobotControl_released(self.leftmultirobotButton.text()))
        self.rightmultirobotButton.released.connect(lambda: self.MultiRobotControl_released(self.leftmultirobotButton.text()))

        self.frontmultirobotButton.setAutoRepeat(True)
        self.backmultirobotButton.setAutoRepeat(True)
        self.rightmultirobotButton.setAutoRepeat(True)
        self.leftmultirobotButton.setAutoRepeat(True)

        #####

        #显示图片
        self.pushButton.clicked.connect(self.showImageLabel)
        self.aubosetEvent()

        self.pointcloudButton.clicked.connect(pointCloudShow.pointcloudshow)


    def setFlag(self):
        self.platform_flag=False
        self.mission_flag=False
        self.multicontrolflag=False
        self.application_flag=False


    #  自定义的槽函数,change selected tabflag
    def tabfun(self,index):
        print "tabfun click" + "  "+str(index)
        self.setFlag()
        if index==0:
            self.platform_flag=True
        elif index==1:
            self.mission_flag=True
        elif index==2:
            self.multicontrolflag=True
        else:
            self.application_flag=True


    # 刷新系统设备在线情况
    def refresh(self):

        self.robotlist = self.iopsys.showRobotList()
        # print "self.robotlist",self.robotlist
    #show config information in gui
    def showConfigInfo(self):

        robotConfigInfo=self.configInfo

        # config base information
        self.configTableWidget.removeColumn(2)
        tabwidgetitem=QtWidgets.QTableWidgetItem(robotConfigInfo["Name"])
        self.configTableWidget.setItem(0,1,tabwidgetitem)
        tabwidgetitem = QtWidgets.QTableWidgetItem(robotConfigInfo["System"])
        self.configTableWidget.setItem(1, 1, tabwidgetitem)
        tabwidgetitem = QtWidgets.QTableWidgetItem(robotConfigInfo["ROSversion"])
        self.configTableWidget.setItem(2, 1, tabwidgetitem)

        rows=self.senserTableWidget.rowCount()
        # self.senserTableWidget.clear()
        for i in range(rows):
            self.senserTableWidget.removeRow(i)

        keys=robotConfigInfo["Payload"].keys()
        self.senserTableWidget.setRowCount(len(keys))
        self.senserTableWidget.setColumnCount(2)
        vhearder=[]

        # self.senserTableWidget
        for i in range(len(robotConfigInfo["Payload"])):
            vhearder.append(str(i+1))
            # self.senserTableWidget.insertRow(i)
            tabwidgetitem = QtWidgets.QTableWidgetItem(keys[i])
            self.senserTableWidget.setItem(i,0,tabwidgetitem)
            tabwidgetitem = QtWidgets.QTableWidgetItem(robotConfigInfo["Payload"][keys[i]])
            self.senserTableWidget.setItem(i, 1, tabwidgetitem)
            # item = self.senserTableWidget.verticalHeaderItem(i)
            # item.setText(str(i + 1))
        self.senserTableWidget.setVerticalHeaderLabels(vhearder)


    # the tab is changed ,the robot clicked event is different
    def robotClickedFun(self):
        if self.platform_flag:
            self.showServiceList()
            self.showConfigInfo()
        elif self.mission_flag:
            #clear the lineedit content
            self.robotnamelineEdit.clear()
            #set the lineEdit content as selected robot name
            self.robotnamelineEdit.setText(self.robotlistTreeWidget.currentItem().text(0))
        elif self.multicontrolflag:
            self.getMultiRobotName()

    ### 群体控制相应的函数    ####
    def getMultiRobotName(self):

        self.multirobotplainTextEdit.clear()
        robotname=self.robotlistTreeWidget.currentItem().text(0)
        if robotname in self.selectedRobotlist.keys():
            self.selectedRobotlist[robotname]^=1
        else:
            self.selectedRobotlist[robotname]=1
        for key in self.selectedRobotlist:
          if self.selectedRobotlist[key]:
              print key
              self.multirobotplainTextEdit.appendPlainText(key)

    #获取多个设备的控制权
    def getMultiRobotAcessControl(self):
        self.selectedRobotlist_ident=[]
        self.multiPub=[]
        for key in self.selectedRobotlist:
          if self.selectedRobotlist[key]:
              self.multiPub.append(rospy.Publisher('/' + key + '/cmd_vel', geometry_msgs.msg.Twist, queue_size=1))
              for robot in self.robotlist:
                  if key==robot.ident.name:
                      self.selectedRobotlist_ident.append(robot.ident)
                      break

        self.iopsys.establishRobotsConnection(self.selectedRobotlist_ident)

        print "多智能体设备控制发布成功"


    def releaseMultiRobotControl(self):
        self.iopsys.cancelRobotsConnection(self.selectedRobotlist_ident)
        print "多智能体设备控制取消成功"


    def MultiRobotControl(self,buttonName):
        move_cmd = Twist()
        if buttonName == "前进":
            print "Key_up is Pressed"
            move_cmd.linear.x = self.multilinearspeed
        elif buttonName == "后退":
            print "Key_down is Pressed"
            move_cmd.linear.x = -self.multilinearspeed
        elif buttonName == "右转":
            print "Key_Right is Pressed"
            move_cmd.angular.z = -self.multiangularspeed
        elif buttonName == "左转":
            print "Key_Left is Pressed"
            move_cmd.angular.z = self.multiangularspeed
        try:
            for pub in self.multiPub:
                pub.publish(move_cmd)
        except:
            print "Publisher is null"
    def MultiRobotControl_released(self,buttonName):
        move_cmd = Twist()
        if buttonName == "前进":
            print "Key_up is Pressed"
            move_cmd.linear.x = 0
        elif buttonName == "后退":
            print "Key_down is Pressed"
            move_cmd.linear.x = 0
        elif buttonName == "右转":
            print "Key_Right is Pressed"
            move_cmd.angular.z = 0
        elif buttonName == "左转":
            print "Key_Left is Pressed"
            move_cmd.angular.z = 0
        try:
            for pub in self.multiPub:
                pub.publish(move_cmd)
        except:
            print "Publisher is null"





    ###########################

    def aubosetEvent(self):
        self.fanwei=[0,1]
        self.currentangular =0
        self.basepushButton.clicked.connect(lambda :self.showaubodata(self.basepushButton.text()))
        self.shouderpushButton.clicked.connect(lambda :self.showaubodata(self.shouderpushButton.text()))
        self.elbowpushButton.clicked.connect(lambda :self.showaubodata(self.elbowpushButton.text()))
        self.wrist1pushButton.clicked.connect(lambda :self.showaubodata(self.wrist1pushButton.text()))
        self.wrist2pushButton.clicked.connect(lambda :self.showaubodata(self.wrist2pushButton.text()))
        self.wrist3pushButton.clicked.connect(lambda :self.showaubodata(self.wrist3pushButton.text()))
        self.aubopluspushButton.clicked.connect(lambda :self.angularPlusSub(self.aubopluspushButton.objectName()))
        self.aubosubpushButton.clicked.connect(lambda :self.angularPlusSub(self.aubosubpushButton.objectName()))
    def showaubodata(self,name):
        if name=="基座/base":
            self.fanwei[0]=-175
            self.fanwei[1]=175
            self.maxspeed=150
        elif name=="肘部/Elbow":
            self.fanwei[0]=-175
            self.fanwei[1]=175
            self.maxspeed=150
        elif name=="肩部/shoulder":
            self.fanwei[0]=-175
            self.fanwei[1]=175
            self.maxspeed=150
        elif name=="腕部/Wrist1":
            self.fanwei[0]=-175
            self.fanwei[1]=175
            self.maxspeed=180
        elif name=="腕部/Wrist2":
            self.fanwei[0]=-175
            self.fanwei[1]=175
            self.maxspeed=180
        else:
            self.fanwei[0] = -175
            self.fanwei[1] = 175
            self.maxspeed = 180
        self.translineEdit.setText(str(self.fanwei[0])+"~"+str(self.fanwei[1]))
        self.maxspeedlineEdit.setText(str(self.maxspeed))
    def angularPlusSub(self,name):
        if name=="aubopluspushButton":
            self.currentangular+=5
            if self.currentangular>175:
                self.currentangular=175
        elif name=="aubosubpushButton":
            self.currentangular -= 5
            if self.currentangular <-175:
                self.currentangular = -175
        self.currentangularlineEdit.setText(str(self.currentangular))

    def auboshowImageLabel(self):
        path="./aubo.png"
        jpg=QtGui.QPixmap(path).scaled(self.aubolabel.width(),self.aubolabel.height())
        self.aubolabel.setPixmap(jpg)

    def showServiceList(self):

        self.serviceTreeWidget.clear()

        robotname=self.robotlistTreeWidget.currentItem()
        print "robotname",self.robotlistTreeWidget.currentItem()
        # robotname.setBackground(0, QtGui.QColor('green'))

        for robot in self.robotlist:
            if robotname.text(0)==robot.ident.name:
                service_platform=QtWidgets.QTreeWidgetItem(self.serviceTreeWidget)
                service_platform.setText(0,"1.平台服务")
                for service in robot.nodes[0].components[0].services:
                    ser=service.uri[13:-1]+" "+str(service.major_version)+"."+str(service.minor_version)
                    tree1=QtWidgets.QTreeWidgetItem(service_platform)
                    tree1.setText(0,ser)
                    tree1.setText(1,"2")
                    tree1.setText(2,"3")
                    
                service_platform.setExpanded(True)
                return
    def agentCon(self):

        print "agentControl"
        robotname = self.robotnamelineEdit.text()
        print "robotname", self.robotlistTreeWidget.currentItem()
        for robot in self.robotlist:
            print robotname == robot.ident.name
            if robotname==robot.ident.name:
                print "zkzkzk"
                print robot.ident
                print self.iopsys.establishConnection(robot.ident)
                self.singleRobotControlPub = rospy.Publisher('/' + robotname + '/cmd_vel', geometry_msgs.msg.Twist, queue_size=1)
                return
    def cancelCon(self):
        print "cancelControl"
        robotname = self.robotnamelineEdit.text()
        print "robotname", self.robotlistTreeWidget.currentItem()
        for robot in self.robotlist:
            print robotname == robot.ident.name
            if robotname == robot.ident.name:
                print robot.ident
                print self.iopsys.cancelConnection(robot.ident)
                return
    def tansEvent(self,buttonName):
        # self.frontButton.setAutoRepeat(True)
        move_cmd = Twist()
        if buttonName=="前进":
            print "Key_up is Pressed"
            move_cmd.linear.x = self.linearspeed
        elif buttonName=="后退":
            print "Key_down is Pressed"
            move_cmd.linear.x = -self.linearspeed
        elif buttonName=="右转":
            print "Key_Right is Pressed"
            move_cmd.angular.z = -self.angularspeed
        elif buttonName=="左转":
            print "Key_Left is Pressed"
            move_cmd.angular.z = self.angularspeed
        try:
            self.singleRobotControlPub.publish(move_cmd)
            print "发布成功"
        except:
            print "Publisher is null"
    def button_releaseed(self,buttonName):

        print  "releaseYYYYYYYYY"
        # self.frontButton.setAutoRepeat(False)
        # for i in range(10):
        move_cmd = Twist()
        if buttonName == "前进":
            print "Key_up is Pressed"
            move_cmd.linear.x = 0
        elif buttonName == "后退":
            print "Key_down is Pressed"
            move_cmd.linear.x = 0
        elif buttonName == "右转":
            print "Key_Right is Pressed"
            move_cmd.angular.z = 0
        elif buttonName == "左转":
            print "Key_Left is Pressed"
            move_cmd.angular.z = 0
        try:
            self.singleRobotControlPub.publish(move_cmd)
            # time.sleep(0.5)
            print "成释放功"
        except:
            print "Publisher is null"


        # 初始化ｒｏｓ

    def init_ros(self):
        rospy.init_node('IopSystem', anonymous=True)

    def platform_server(self, robotlist):
        # 1.clear the widget list
        # print "platform_server", robotlist
        str="vnfjdksnvdkjs"
        self.robotlistTreeWidget.clear()

        self.uavlistTree = QtWidgets.QTreeWidgetItem(self.robotlistTreeWidget)
        self.uavlistTree.setText(0, "无人车")
        self.ugvlistTree = QtWidgets.QTreeWidgetItem(self.robotlistTreeWidget)
        self.ugvlistTree.setText(0, "无人机")

        self.platform_server_trwidget = []
        for robot in robotlist:
            # print "platform", robot.ident.name

            if "M210" in robot.ident.name:
                subchild1 = QtWidgets.QTreeWidgetItem(self.ugvlistTree)
                subchild1.setText(0, robot.ident.name)
            else:
                subchild = QtWidgets.QTreeWidgetItem(self.uavlistTree)
                subchild.setText(0, robot.ident.name)


            # self.platform_server_trwidget.clicked.connect(lambda :self.showServiceList(self.pl))
        self.uavlistTree.setExpanded(True)
        self.ugvlistTree.setExpanded(True)
    #修改进度条数字改变事件
    #
    def addverticalSlider(self,verticalSlider):
        verticalSlider.setValue(verticalSlider.value()+5)
    def subverticalSlider(self,verticalSlider):
        verticalSlider.setValue(verticalSlider.value()-5)
    def changedLinear_angular(self):
        # 线速度
        self.linearspeed = round(3.5 * self.linearverticalSlider.value() / self.linearverticalSlider.maximum(), 1)
        # 角速度
        self.angularspeed = round(1.5 * self.angularverticalSlider.value() / self.angularverticalSlider.maximum(), 1)
        self.linearshowlabel.setText("%.1f"%(3.5*self.linearverticalSlider.value()/self.linearverticalSlider.maximum())+"m/s")
        self.angularshowlabel.setText("%.1f"%(1.5*self.angularverticalSlider.value()/self.angularverticalSlider.maximum())+"rad/s")

    def changedMultiLinear_angular(self):
        # 线速度
        self.multilinearspeed = round(3.5 * self.linearmultirobotverticalSlider.value() / self.linearmultirobotverticalSlider.maximum(), 1)
        # 角速度
        self.multiangularspeed = round(1.5 * self.angularmultirobotverticalSlider.value() / self.angularmultirobotverticalSlider.maximum(), 1)
        self.linearmultirobotshowlabel.setText(
            "%.1f" % (3.5 * self.linearmultirobotverticalSlider.value() / self.linearmultirobotverticalSlider.maximum()) + "m/s")
        self.angularmultirobotshowlabel.setText(
            "%.1f" % (1.5 * self.angularmultirobotverticalSlider.value() / self.angularmultirobotverticalSlider.maximum()) + "rad/s")
    ## 显示图传画面
    def showImageLabel(self):
        path="./2020.png"
        jpg=QtGui.QPixmap(path).scaled(self.showimagelabel.width(),self.showimagelabel.height())
        # self.showimagelabel.setPixmap(jpg)
        # threading.Thread(target=self.displayWebcam()).start()
        self.displayWebcam()
        # pass
    def callback(self,data):
        # define picture to_down' coefficient of ratio
        # print data
        # print "sdfsdfsfsfesrewr"
        self.img = self.bridge.compressed_imgmsg_to_cv2(data, "bgr8")
        # %.6f表示小数点后带有6位，可根据精确度需要修改；
        # image_name = timestr + ".jpg"  # 图像命名：时间戳.jpg
        # cv2.imwrite(self.cam0_path + image_name, cv_img)  # 保存；
        # cv2.imshow("frame", cv_img)
        #
        # cv2.waitKey(3)
        # self.img=cv2.blur(cv_img,(self.showimagelabel.width(),self.showimagelabel.height()))
        # self.img=cv2.resize(cv_img,(self.showimagelabel.width(),self.showimagelabel.height()))
        height,width,channel=self.img.shape
        showimage=QtGui.QImage(self.img.data,width,height,width*3,QtGui.QImage.Format_RGB888).rgbSwapped()
        # jpg=QtGui.QPixmap(self.cam0_path+image_name).scaled(self.showimagelabel.width(),self.showimagelabel.height())
        self.showimagelabel.setPixmap(QtGui.QPixmap.fromImage(showimage))
        # time.sleep(0.5)

    def displayWebcam(self):
        # rospy.init_node('webcam_display', anonymous=True)
        # make a video_object and init the video object
        rospy.Subscriber('/front/compressed', CompressedImage, self.callback)
        # print "wqerhwkfjwihvs"
        # rospy.spin()

    #加载点云数据
    def showPointCloud(self):

        pass


    #######
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(856, 734)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.robotlistTreeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.robotlistTreeWidget.setGeometry(QtCore.QRect(20, 20, 251, 431))
        self.robotlistTreeWidget.setObjectName("robotlistTreeWidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(280, 20, 551, 431))
        self.tabWidget.setObjectName("tabWidget")
        self.platform = QtWidgets.QWidget()
        self.platform.setObjectName("platform")
        self.serviceTreeWidget = QtWidgets.QTreeWidget(self.platform)
        self.serviceTreeWidget.setGeometry(QtCore.QRect(20, 140, 491, 241))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.serviceTreeWidget.sizePolicy().hasHeightForWidth())
        self.serviceTreeWidget.setSizePolicy(sizePolicy)
        self.serviceTreeWidget.setLineWidth(1)
        self.serviceTreeWidget.setObjectName("serviceTreeWidget")
        self.configTableWidget = QtWidgets.QTableWidget(self.platform)
        self.configTableWidget.setGeometry(QtCore.QRect(20, 0, 211, 131))
        self.configTableWidget.setObjectName("configTableWidget")
        self.configTableWidget.setColumnCount(2)
        self.configTableWidget.setRowCount(3)
        item = QtWidgets.QTableWidgetItem()
        self.configTableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.configTableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.configTableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.configTableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.configTableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.configTableWidget.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.configTableWidget.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.configTableWidget.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.configTableWidget.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.configTableWidget.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.configTableWidget.setItem(2, 1, item)
        self.senserTableWidget = QtWidgets.QTableWidget(self.platform)
        self.senserTableWidget.setGeometry(QtCore.QRect(270, 0, 241, 121))
        self.senserTableWidget.setObjectName("senserTableWidget")
        self.senserTableWidget.setColumnCount(2)
        self.senserTableWidget.setRowCount(4)
        item = QtWidgets.QTableWidgetItem()
        self.senserTableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.senserTableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.senserTableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.senserTableWidget.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.senserTableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.senserTableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.senserTableWidget.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.senserTableWidget.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.senserTableWidget.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.senserTableWidget.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.senserTableWidget.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.senserTableWidget.setItem(2, 1, item)
        self.tabWidget.addTab(self.platform, "")
        self.mission = QtWidgets.QWidget()
        self.mission.setObjectName("mission")
        self.selectedRobotNmae = QtWidgets.QLabel(self.mission)
        self.selectedRobotNmae.setGeometry(QtCore.QRect(10, 20, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setItalic(True)
        self.selectedRobotNmae.setFont(font)
        self.selectedRobotNmae.setObjectName("selectedRobotNmae")
        self.robotnamelineEdit = QtWidgets.QLineEdit(self.mission)
        self.robotnamelineEdit.setGeometry(QtCore.QRect(120, 20, 231, 31))
        self.robotnamelineEdit.setMaxLength(32761)
        self.robotnamelineEdit.setReadOnly(False)
        self.robotnamelineEdit.setObjectName("robotnamelineEdit")
        self.okButton = QtWidgets.QPushButton(self.mission)
        self.okButton.setGeometry(QtCore.QRect(120, 50, 101, 31))
        self.okButton.setObjectName("okButton")
        self.cancelcontrolButton = QtWidgets.QPushButton(self.mission)
        self.cancelcontrolButton.setGeometry(QtCore.QRect(250, 50, 101, 31))
        self.cancelcontrolButton.setObjectName("cancelcontrolButton")
        self.frontButton = QtWidgets.QPushButton(self.mission)
        self.frontButton.setGeometry(QtCore.QRect(140, 130, 71, 61))
        self.frontButton.setObjectName("frontButton")
        self.rightButton = QtWidgets.QPushButton(self.mission)
        self.rightButton.setGeometry(QtCore.QRect(210, 190, 71, 61))
        self.rightButton.setObjectName("rightButton")
        self.backButton = QtWidgets.QPushButton(self.mission)
        self.backButton.setGeometry(QtCore.QRect(140, 250, 71, 61))
        self.backButton.setObjectName("backButton")
        self.leftButton = QtWidgets.QPushButton(self.mission)
        self.leftButton.setGeometry(QtCore.QRect(70, 190, 71, 61))
        self.leftButton.setObjectName("leftButton")
        self.linearverticalSlider = QtWidgets.QSlider(self.mission)
        self.linearverticalSlider.setGeometry(QtCore.QRect(350, 120, 51, 221))
        self.linearverticalSlider.setMaximum(70)
        self.linearverticalSlider.setSingleStep(5)
        self.linearverticalSlider.setSliderPosition(30)
        self.linearverticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.linearverticalSlider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.linearverticalSlider.setTickInterval(2)
        self.linearverticalSlider.setObjectName("linearverticalSlider")
        self.linearplusButton = QtWidgets.QPushButton(self.mission)
        self.linearplusButton.setGeometry(QtCore.QRect(320, 120, 31, 27))
        self.linearplusButton.setObjectName("linearplusButton")
        self.linearsubButton = QtWidgets.QPushButton(self.mission)
        self.linearsubButton.setGeometry(QtCore.QRect(320, 310, 31, 27))
        self.linearsubButton.setObjectName("linearsubButton")
        self.linarvelocitylabel = QtWidgets.QLabel(self.mission)
        self.linarvelocitylabel.setGeometry(QtCore.QRect(350, 90, 67, 31))
        self.linarvelocitylabel.setObjectName("linarvelocitylabel")
        self.linearshowlabel = QtWidgets.QLabel(self.mission)
        self.linearshowlabel.setGeometry(QtCore.QRect(350, 350, 61, 31))
        self.linearshowlabel.setObjectName("linearshowlabel")
        self.angularlabel = QtWidgets.QLabel(self.mission)
        self.angularlabel.setGeometry(QtCore.QRect(470, 90, 67, 31))
        self.angularlabel.setObjectName("angularlabel")
        self.angularshowlabel = QtWidgets.QLabel(self.mission)
        self.angularshowlabel.setGeometry(QtCore.QRect(460, 350, 71, 31))
        self.angularshowlabel.setObjectName("angularshowlabel")
        self.angularsubButton = QtWidgets.QPushButton(self.mission)
        self.angularsubButton.setGeometry(QtCore.QRect(440, 310, 31, 27))
        self.angularsubButton.setObjectName("angularsubButton")
        self.angularverticalSlider = QtWidgets.QSlider(self.mission)
        self.angularverticalSlider.setGeometry(QtCore.QRect(470, 120, 51, 221))
        self.angularverticalSlider.setMaximum(70)
        self.angularverticalSlider.setSingleStep(5)
        self.angularverticalSlider.setSliderPosition(30)
        self.angularverticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.angularverticalSlider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.angularverticalSlider.setTickInterval(2)
        self.angularverticalSlider.setObjectName("angularverticalSlider")
        self.angularplusButton = QtWidgets.QPushButton(self.mission)
        self.angularplusButton.setGeometry(QtCore.QRect(440, 120, 31, 27))
        self.angularplusButton.setObjectName("angularplusButton")
        self.tabWidget.addTab(self.mission, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(10, 10, 81, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.multirobotplainTextEdit = QtWidgets.QPlainTextEdit(self.tab)
        self.multirobotplainTextEdit.setGeometry(QtCore.QRect(100, 10, 391, 81))
        self.multirobotplainTextEdit.setObjectName("multirobotplainTextEdit")
        self.frontmultirobotButton = QtWidgets.QPushButton(self.tab)
        self.frontmultirobotButton.setGeometry(QtCore.QRect(240, 180, 71, 61))
        self.frontmultirobotButton.setObjectName("frontmultirobotButton")
        self.rightmultirobotButton = QtWidgets.QPushButton(self.tab)
        self.rightmultirobotButton.setGeometry(QtCore.QRect(310, 240, 71, 61))
        self.rightmultirobotButton.setObjectName("rightmultirobotButton")
        self.backmultirobotButton = QtWidgets.QPushButton(self.tab)
        self.backmultirobotButton.setGeometry(QtCore.QRect(240, 300, 71, 61))
        self.backmultirobotButton.setObjectName("backmultirobotButton")
        self.leftmultirobotButton = QtWidgets.QPushButton(self.tab)
        self.leftmultirobotButton.setGeometry(QtCore.QRect(170, 240, 71, 61))
        self.leftmultirobotButton.setObjectName("leftmultirobotButton")
        self.linearmultirobotsubButton = QtWidgets.QPushButton(self.tab)
        self.linearmultirobotsubButton.setGeometry(QtCore.QRect(30, 330, 31, 27))
        self.linearmultirobotsubButton.setObjectName("linearmultirobotsubButton")
        self.linearmultirobotplusButton = QtWidgets.QPushButton(self.tab)
        self.linearmultirobotplusButton.setGeometry(QtCore.QRect(30, 140, 31, 27))
        self.linearmultirobotplusButton.setObjectName("linearmultirobotplusButton")
        self.linearmultirobotverticalSlider = QtWidgets.QSlider(self.tab)
        self.linearmultirobotverticalSlider.setGeometry(QtCore.QRect(60, 140, 51, 221))
        self.linearmultirobotverticalSlider.setMaximum(70)
        self.linearmultirobotverticalSlider.setSingleStep(5)
        self.linearmultirobotverticalSlider.setSliderPosition(30)
        self.linearmultirobotverticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.linearmultirobotverticalSlider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.linearmultirobotverticalSlider.setTickInterval(2)
        self.linearmultirobotverticalSlider.setObjectName("linearmultirobotverticalSlider")
        self.linarmultirobotvelocitylabel = QtWidgets.QLabel(self.tab)
        self.linarmultirobotvelocitylabel.setGeometry(QtCore.QRect(60, 110, 67, 31))
        self.linarmultirobotvelocitylabel.setObjectName("linarmultirobotvelocitylabel")
        self.linearmultirobotshowlabel = QtWidgets.QLabel(self.tab)
        self.linearmultirobotshowlabel.setGeometry(QtCore.QRect(60, 370, 61, 31))
        self.linearmultirobotshowlabel.setObjectName("linearmultirobotshowlabel")
        self.angularmultirobotshowlabel = QtWidgets.QLabel(self.tab)
        self.angularmultirobotshowlabel.setGeometry(QtCore.QRect(470, 370, 81, 31))
        self.angularmultirobotshowlabel.setObjectName("angularmultirobotshowlabel")
        self.angularmultirobotplusButton = QtWidgets.QPushButton(self.tab)
        self.angularmultirobotplusButton.setGeometry(QtCore.QRect(440, 140, 31, 27))
        self.angularmultirobotplusButton.setObjectName("angularmultirobotplusButton")
        self.angularmultirobotlabel = QtWidgets.QLabel(self.tab)
        self.angularmultirobotlabel.setGeometry(QtCore.QRect(470, 110, 67, 31))
        self.angularmultirobotlabel.setObjectName("angularmultirobotlabel")
        self.angularmultirobotsubButton = QtWidgets.QPushButton(self.tab)
        self.angularmultirobotsubButton.setGeometry(QtCore.QRect(440, 330, 31, 27))
        self.angularmultirobotsubButton.setObjectName("angularmultirobotsubButton")
        self.angularmultirobotverticalSlider = QtWidgets.QSlider(self.tab)
        self.angularmultirobotverticalSlider.setGeometry(QtCore.QRect(470, 140, 51, 221))
        self.angularmultirobotverticalSlider.setMaximum(70)
        self.angularmultirobotverticalSlider.setSingleStep(5)
        self.angularmultirobotverticalSlider.setSliderPosition(30)
        self.angularmultirobotverticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.angularmultirobotverticalSlider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.angularmultirobotverticalSlider.setTickInterval(2)
        self.angularmultirobotverticalSlider.setObjectName("angularmultirobotverticalSlider")
        self.multirobotcancelcontrolButton = QtWidgets.QPushButton(self.tab)
        self.multirobotcancelcontrolButton.setGeometry(QtCore.QRect(300, 120, 101, 31))
        self.multirobotcancelcontrolButton.setObjectName("multirobotcancelcontrolButton")
        self.multirobotokButton = QtWidgets.QPushButton(self.tab)
        self.multirobotokButton.setGeometry(QtCore.QRect(170, 120, 101, 31))
        self.multirobotokButton.setObjectName("multirobotokButton")
        self.line = QtWidgets.QFrame(self.tab)
        self.line.setGeometry(QtCore.QRect(20, 89, 501, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.line.setFont(font)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.tabWidget.addTab(self.tab, "")
        self.mutileControl = QtWidgets.QWidget()
        self.mutileControl.setObjectName("mutileControl")
        self.groupBox3_2 = QtWidgets.QGroupBox(self.mutileControl)
        self.groupBox3_2.setGeometry(QtCore.QRect(40, 230, 471, 91))
        self.groupBox3_2.setTitle("")
        self.groupBox3_2.setObjectName("groupBox3_2")
        self.label_7 = QtWidgets.QLabel(self.groupBox3_2)
        self.label_7.setGeometry(QtCore.QRect(10, 20, 54, 12))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.groupBox3_2)
        self.label_8.setGeometry(QtCore.QRect(10, 50, 54, 12))
        self.label_8.setObjectName("label_8")
        self.ugvLineEdit_2 = QtWidgets.QLineEdit(self.groupBox3_2)
        self.ugvLineEdit_2.setGeometry(QtCore.QRect(40, 40, 113, 20))
        self.ugvLineEdit_2.setObjectName("ugvLineEdit_2")
        self.uavLineEdit_2 = QtWidgets.QLineEdit(self.groupBox3_2)
        self.uavLineEdit_2.setGeometry(QtCore.QRect(40, 10, 111, 20))
        self.uavLineEdit_2.setObjectName("uavLineEdit_2")
        self.lineEdit_8 = QtWidgets.QLineEdit(self.groupBox3_2)
        self.lineEdit_8.setGeometry(QtCore.QRect(40, 10, 113, 20))
        self.lineEdit_8.setObjectName("lineEdit_8")
        self.collaborationControlButton_2 = QtWidgets.QPushButton(self.groupBox3_2)
        self.collaborationControlButton_2.setGeometry(QtCore.QRect(340, 40, 75, 23))
        self.collaborationControlButton_2.setObjectName("collaborationControlButton_2")
        self.collaborationOkButton_2 = QtWidgets.QPushButton(self.groupBox3_2)
        self.collaborationOkButton_2.setGeometry(QtCore.QRect(220, 40, 75, 23))
        self.collaborationOkButton_2.setObjectName("collaborationOkButton_2")
        self.groupBox2_2 = QtWidgets.QGroupBox(self.mutileControl)
        self.groupBox2_2.setGeometry(QtCore.QRect(40, 90, 471, 91))
        self.groupBox2_2.setTitle("")
        self.groupBox2_2.setObjectName("groupBox2_2")
        self.label_9 = QtWidgets.QLabel(self.groupBox2_2)
        self.label_9.setGeometry(QtCore.QRect(10, 20, 21, 21))
        self.label_9.setObjectName("label_9")
        self.mainRobotLineEdit_2 = QtWidgets.QLineEdit(self.groupBox2_2)
        self.mainRobotLineEdit_2.setGeometry(QtCore.QRect(50, 20, 113, 20))
        self.mainRobotLineEdit_2.setObjectName("mainRobotLineEdit_2")
        self.label_10 = QtWidgets.QLabel(self.groupBox2_2)
        self.label_10.setGeometry(QtCore.QRect(190, 20, 21, 16))
        self.label_10.setObjectName("label_10")
        self.slaveRobotLineEdit_2 = QtWidgets.QLineEdit(self.groupBox2_2)
        self.slaveRobotLineEdit_2.setGeometry(QtCore.QRect(222, 20, 191, 20))
        self.slaveRobotLineEdit_2.setObjectName("slaveRobotLineEdit_2")
        self.label_11 = QtWidgets.QLabel(self.groupBox2_2)
        self.label_11.setGeometry(QtCore.QRect(10, 50, 41, 16))
        self.label_11.setObjectName("label_11")
        self.formationComboBox_2 = QtWidgets.QComboBox(self.groupBox2_2)
        self.formationComboBox_2.setGeometry(QtCore.QRect(50, 50, 131, 22))
        self.formationComboBox_2.setObjectName("formationComboBox_2")
        self.formationComboBox_2.addItem("")
        self.formationComboBox_2.addItem("")
        self.formationOkButton_2 = QtWidgets.QPushButton(self.groupBox2_2)
        self.formationOkButton_2.setGeometry(QtCore.QRect(220, 50, 75, 23))
        self.formationOkButton_2.setObjectName("formationOkButton_2")
        self.formationControlButton_2 = QtWidgets.QPushButton(self.groupBox2_2)
        self.formationControlButton_2.setGeometry(QtCore.QRect(340, 50, 75, 23))
        self.formationControlButton_2.setObjectName("formationControlButton_2")
        self.formationRadioButton_2 = QtWidgets.QRadioButton(self.mutileControl)
        self.formationRadioButton_2.setGeometry(QtCore.QRect(40, 70, 89, 16))
        self.formationRadioButton_2.setObjectName("formationRadioButton_2")
        self.collaborationRadioButton_2 = QtWidgets.QRadioButton(self.mutileControl)
        self.collaborationRadioButton_2.setGeometry(QtCore.QRect(40, 210, 89, 16))
        self.collaborationRadioButton_2.setObjectName("collaborationRadioButton_2")
        self.tabWidget.addTab(self.mutileControl, "")
        self.showimageTab = QtWidgets.QWidget()
        self.showimageTab.setObjectName("showimageTab")
        self.showimagelabel = QtWidgets.QLabel(self.showimageTab)
        self.showimagelabel.setGeometry(QtCore.QRect(30, 20, 501, 311))
        self.showimagelabel.setText("")
        self.showimagelabel.setObjectName("showimagelabel")
        self.pushButton = QtWidgets.QPushButton(self.showimageTab)
        self.pushButton.setGeometry(QtCore.QRect(300, 360, 181, 31))
        self.pushButton.setObjectName("pushButton")
        self.pointcloudButton = QtWidgets.QPushButton(self.showimageTab)
        self.pointcloudButton.setGeometry(QtCore.QRect(50, 360, 181, 31))
        self.pointcloudButton.setObjectName("pointcloudButton")
        self.tabWidget.addTab(self.showimageTab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.aubolabel = QtWidgets.QLabel(self.tab_2)
        self.aubolabel.setGeometry(QtCore.QRect(30, 30, 221, 321))
        self.aubolabel.setText("")
        self.aubolabel.setObjectName("aubolabel")
        self.basepushButton = QtWidgets.QPushButton(self.tab_2)
        self.basepushButton.setGeometry(QtCore.QRect(300, 80, 99, 41))
        self.basepushButton.setObjectName("basepushButton")
        self.shouderpushButton = QtWidgets.QPushButton(self.tab_2)
        self.shouderpushButton.setGeometry(QtCore.QRect(300, 200, 99, 41))
        self.shouderpushButton.setObjectName("shouderpushButton")
        self.elbowpushButton = QtWidgets.QPushButton(self.tab_2)
        self.elbowpushButton.setGeometry(QtCore.QRect(300, 140, 99, 41))
        self.elbowpushButton.setObjectName("elbowpushButton")
        self.wrist1pushButton = QtWidgets.QPushButton(self.tab_2)
        self.wrist1pushButton.setGeometry(QtCore.QRect(430, 80, 99, 41))
        self.wrist1pushButton.setObjectName("wrist1pushButton")
        self.wrist2pushButton = QtWidgets.QPushButton(self.tab_2)
        self.wrist2pushButton.setGeometry(QtCore.QRect(430, 140, 99, 41))
        self.wrist2pushButton.setObjectName("wrist2pushButton")
        self.wrist3pushButton = QtWidgets.QPushButton(self.tab_2)
        self.wrist3pushButton.setGeometry(QtCore.QRect(430, 200, 99, 41))
        self.wrist3pushButton.setObjectName("wrist3pushButton")
        self.label_3 = QtWidgets.QLabel(self.tab_2)
        self.label_3.setGeometry(QtCore.QRect(300, 10, 71, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.translineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.translineEdit.setGeometry(QtCore.QRect(380, 10, 161, 27))
        self.translineEdit.setObjectName("translineEdit")
        self.label_4 = QtWidgets.QLabel(self.tab_2)
        self.label_4.setGeometry(QtCore.QRect(300, 50, 71, 17))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.maxspeedlineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.maxspeedlineEdit.setGeometry(QtCore.QRect(380, 40, 161, 27))
        self.maxspeedlineEdit.setObjectName("maxspeedlineEdit")
        self.aubopluspushButton = QtWidgets.QPushButton(self.tab_2)
        self.aubopluspushButton.setGeometry(QtCore.QRect(330, 250, 71, 61))
        font = QtGui.QFont()
        font.setPointSize(23)
        font.setBold(True)
        font.setWeight(75)
        self.aubopluspushButton.setFont(font)
        self.aubopluspushButton.setObjectName("aubopluspushButton")
        self.aubosubpushButton = QtWidgets.QPushButton(self.tab_2)
        self.aubosubpushButton.setGeometry(QtCore.QRect(430, 250, 71, 61))
        font = QtGui.QFont()
        font.setPointSize(23)
        font.setBold(True)
        font.setWeight(75)
        self.aubosubpushButton.setFont(font)
        self.aubosubpushButton.setObjectName("aubosubpushButton")
        self.currentangularlineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.currentangularlineEdit.setGeometry(QtCore.QRect(380, 340, 161, 27))
        self.currentangularlineEdit.setObjectName("currentangularlineEdit")
        self.label_20 = QtWidgets.QLabel(self.tab_2)
        self.label_20.setGeometry(QtCore.QRect(300, 340, 71, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_20.setFont(font)
        self.label_20.setObjectName("label_20")
        self.tabWidget.addTab(self.tab_2, "")
        self.logtabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.logtabWidget.setGeometry(QtCore.QRect(20, 460, 821, 221))
        self.logtabWidget.setObjectName("logtabWidget")
        self.logshowTabwidget = QtWidgets.QWidget()
        self.logshowTabwidget.setObjectName("logshowTabwidget")
        self.logtextEdit = QtWidgets.QTextEdit(self.logshowTabwidget)
        self.logtextEdit.setGeometry(QtCore.QRect(0, 0, 821, 211))
        self.logtextEdit.setObjectName("logtextEdit")
        self.logtabWidget.addTab(self.logshowTabwidget, "")
        self.tabWidget.raise_()
        self.robotlistTreeWidget.raise_()
        self.logtabWidget.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 856, 31))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.logtabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.robotlistTreeWidget.headerItem().setText(0, _translate("MainWindow", "平台列表"))
        self.serviceTreeWidget.headerItem().setText(0, _translate("MainWindow", "服务列表                                                              "))
        self.serviceTreeWidget.headerItem().setText(1, _translate("MainWindow", "状态"))
        self.serviceTreeWidget.headerItem().setText(2, _translate("MainWindow", "操作"))
        item = self.configTableWidget.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.configTableWidget.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.configTableWidget.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "3"))
        item = self.configTableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "项目"))
        item = self.configTableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "详情"))
        __sortingEnabled = self.configTableWidget.isSortingEnabled()
        self.configTableWidget.setSortingEnabled(False)
        item = self.configTableWidget.item(0, 0)
        item.setText(_translate("MainWindow", "型号"))
        item = self.configTableWidget.item(1, 0)
        item.setText(_translate("MainWindow", "操作系统"))
        item = self.configTableWidget.item(2, 0)
        item.setText(_translate("MainWindow", "ROS"))
        self.configTableWidget.setSortingEnabled(__sortingEnabled)
        item = self.senserTableWidget.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.senserTableWidget.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.senserTableWidget.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "3"))
        item = self.senserTableWidget.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "4"))
        item = self.senserTableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "载荷"))
        item = self.senserTableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "详情"))
        __sortingEnabled = self.senserTableWidget.isSortingEnabled()
        self.senserTableWidget.setSortingEnabled(False)
        item = self.senserTableWidget.item(0, 0)
        item.setText(_translate("MainWindow", "激光雷达"))
        item = self.senserTableWidget.item(0, 1)
        item.setText(_translate("MainWindow", "LIDAS"))
        item = self.senserTableWidget.item(1, 0)
        item.setText(_translate("MainWindow", "图传"))
        item = self.senserTableWidget.item(1, 1)
        item.setText(_translate("MainWindow", "YIKUN"))
        item = self.senserTableWidget.item(2, 0)
        item.setText(_translate("MainWindow", "定位"))
        item = self.senserTableWidget.item(2, 1)
        item.setText(_translate("MainWindow", "RTK"))
        self.senserTableWidget.setSortingEnabled(__sortingEnabled)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.platform), _translate("MainWindow", "平台管理"))
        self.selectedRobotNmae.setText(_translate("MainWindow", "选择设备名："))
        self.robotnamelineEdit.setText(_translate("MainWindow", "Bulldog"))
        self.okButton.setText(_translate("MainWindow", "确认控制"))
        self.cancelcontrolButton.setText(_translate("MainWindow", "取消控制"))
        self.frontButton.setText(_translate("MainWindow", "前进"))
        self.rightButton.setText(_translate("MainWindow", "右转"))
        self.backButton.setText(_translate("MainWindow", "后退"))
        self.leftButton.setText(_translate("MainWindow", "左转"))
        self.linearplusButton.setText(_translate("MainWindow", "+"))
        self.linearsubButton.setText(_translate("MainWindow", "-"))
        self.linarvelocitylabel.setText(_translate("MainWindow", "线速度"))
        self.linearshowlabel.setText(_translate("MainWindow", "１m/s"))
        self.angularlabel.setText(_translate("MainWindow", "角速度"))
        self.angularshowlabel.setText(_translate("MainWindow", "１rad/s"))
        self.angularsubButton.setText(_translate("MainWindow", "-"))
        self.angularplusButton.setText(_translate("MainWindow", "+"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.mission), _translate("MainWindow", "单体控制"))
        self.label.setText(_translate("MainWindow", "设备列表"))
        self.frontmultirobotButton.setText(_translate("MainWindow", "前进"))
        self.rightmultirobotButton.setText(_translate("MainWindow", "右转"))
        self.backmultirobotButton.setText(_translate("MainWindow", "后退"))
        self.leftmultirobotButton.setText(_translate("MainWindow", "左转"))
        self.linearmultirobotsubButton.setText(_translate("MainWindow", "-"))
        self.linearmultirobotplusButton.setText(_translate("MainWindow", "+"))
        self.linarmultirobotvelocitylabel.setText(_translate("MainWindow", "线速度"))
        self.linearmultirobotshowlabel.setText(_translate("MainWindow", "１m/s"))
        self.angularmultirobotshowlabel.setText(_translate("MainWindow", "１rad/s"))
        self.angularmultirobotplusButton.setText(_translate("MainWindow", "+"))
        self.angularmultirobotlabel.setText(_translate("MainWindow", "角速度"))
        self.angularmultirobotsubButton.setText(_translate("MainWindow", "-"))
        self.multirobotcancelcontrolButton.setText(_translate("MainWindow", "取消控制"))
        self.multirobotokButton.setText(_translate("MainWindow", "确认控制"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "群体控制"))
        self.label_7.setText(_translate("MainWindow", "空："))
        self.label_8.setText(_translate("MainWindow", "地："))
        self.ugvLineEdit_2.setText(_translate("MainWindow", "Bulldog"))
        self.uavLineEdit_2.setText(_translate("MainWindow", "M210"))
        self.lineEdit_8.setText(_translate("MainWindow", "M210"))
        self.collaborationControlButton_2.setText(_translate("MainWindow", "控制"))
        self.collaborationOkButton_2.setText(_translate("MainWindow", "确定"))
        self.label_9.setText(_translate("MainWindow", "主："))
        self.mainRobotLineEdit_2.setText(_translate("MainWindow", "Bulldog"))
        self.label_10.setText(_translate("MainWindow", "从："))
        self.slaveRobotLineEdit_2.setText(_translate("MainWindow", "TB-1、TB-2"))
        self.label_11.setText(_translate("MainWindow", "队形："))
        self.formationComboBox_2.setItemText(0, _translate("MainWindow", "纵队突击"))
        self.formationComboBox_2.setItemText(1, _translate("MainWindow", "箭头队形"))
        self.formationOkButton_2.setText(_translate("MainWindow", "确定"))
        self.formationControlButton_2.setText(_translate("MainWindow", "控制"))
        self.formationRadioButton_2.setText(_translate("MainWindow", "编队控制"))
        self.collaborationRadioButton_2.setText(_translate("MainWindow", "空地协同"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.mutileControl), _translate("MainWindow", "任务管理"))
        self.pushButton.setText(_translate("MainWindow", "画面显示"))
        self.pointcloudButton.setText(_translate("MainWindow", "点云显示"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.showimageTab), _translate("MainWindow", "图传画面"))
        self.basepushButton.setText(_translate("MainWindow", "基座/base"))
        self.shouderpushButton.setText(_translate("MainWindow", "肩部/shoulder"))
        self.elbowpushButton.setText(_translate("MainWindow", "肘部/Elbow"))
        self.wrist1pushButton.setText(_translate("MainWindow", "腕部/Wrist1"))
        self.wrist2pushButton.setText(_translate("MainWindow", "腕部/Wrist2"))
        self.wrist3pushButton.setText(_translate("MainWindow", "腕部/Wrist3"))
        self.label_3.setText(_translate("MainWindow", "运动范围："))
        self.label_4.setText(_translate("MainWindow", "最大速度："))
        self.aubopluspushButton.setText(_translate("MainWindow", "＋"))
        self.aubosubpushButton.setText(_translate("MainWindow", "－"))
        self.label_20.setText(_translate("MainWindow", "当前角度："))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "机械臂控制"))
        self.logtabWidget.setTabText(self.logtabWidget.indexOf(self.logshowTabwidget), _translate("MainWindow", "日志信息"))


    def otherWidget(self):
        self.uavlistTree = QtWidgets.QTreeWidgetItem(self.robotlistTreeWidget)
        self.uavlistTree.setText(0, "无人车")
        self.ugvlistTree = QtWidgets.QTreeWidgetItem(self.robotlistTreeWidget)
        self.ugvlistTree.setText(0, "无人机")
        self.tabWidget.setCurrentWidget(self.platform)
    #set platform info

    ###log info print
    def coloredTextout(self, message):
        print message
        if message[1:5] == "[31m":
            self.logtextEdit.setTextColor(QtGui.QColor(255, 0, 0))
            self.logtextEdit.append(message[5:-5])
        elif message[1:5] == "[32m":
            self.logtextEdit.setTextColor(QtGui.QColor(0, 255, 0))
            self.logtextEdit.append(message[5:-5])
        elif message[1:4] == "[0m":
            self.logtextEdit.setTextColor(QtGui.QColor(0, 0, 0))
            self.logtextEdit.append(message[4:-4])
        else:
            self.logtextEdit.setTextColor(QtGui.QColor(0, 0, 0))
            self.logtextEdit.insertPlainText(message)
        self.logtextEdit.setFocus()

    @QtCore.pyqtSlot(str)
    def upDateMessage(self, message):
        # print("sdfsfds")
        # print(message)
        # self.terminal.append(message)
        # self.textEdit.insertPlainText(message)
        self.coloredTextout(message)
    ######


class QTProcessThread(QtCore.QThread):
    updateSig = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(QTProcessThread, self).__init__(parent)

    def run(self):
        cmd = " roslaunch fkie_iop_cfg_sim_turtle control.launch"

        # cmd = 'ping 127.0.0.1'
        print(cmd)
        mytask = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        while True:
            line = mytask.stdout.readline()
            # print("zkzk")
            if not line:
                break
            x = line.decode('gb2312')
            # print("%s"%x)
            # print(x)
            self.updateSig.emit(x)




if __name__ == '__main__':

    import sys
    #create an application for the gui
    app=QtWidgets.QApplication(sys.argv)

    mWin=QtWidgets.QMainWindow()
    ui=Ui_MainWindow(mWin)

    mWin.show()

    sys.exit(app.exec_())


