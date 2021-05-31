# -*- coding: UTF-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import sys, os
import subprocess

#两个网址
#下面这个把所有的print操作打印到了textedit里
#https://stackoverflow.com/questions/19855288/duplicate-stdout-stderr-in-qtextedit-widget
#下面这个可以实时输出一条命令的结果
#https://fishc.com.cn/thread-75226-1-1.html
#用第二个网址基本够了，再配合颜色判断

class OutputWrapper(QObject):
    outputWritten = pyqtSignal(object, object)

    def __init__(self, parent, stdout=True):
        QObject.__init__(self, parent)
        if stdout:
            self._stream = sys.stdout
            sys.stdout = self
        else:
            self._stream = sys.stderr
            sys.stderr = self
        self._stdout = stdout

    def write(self, text):
        self._stream.write(text)
        self.outputWritten.emit(text, self._stdout)

    def __getattr__(self, name):
        return getattr(self._stream, name)

    # def __del__(self):
    #     try:
    #         if self._stdout:
    #             sys.stdout = self._stream
    #         else:
    #             sys.stderr = self._stream
    #     except AttributeError:
    #         passroslaunch fkie_iop_cfg_sim_turtle control2.launch


class QTProcessThread(QThread):
    updateSig = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super(QTProcessThread, self).__init__(parent)
    def run(self):
        cmd = " roslaunch fkie_iop_cfg_sim_turtle control2.launch"

        
        # cmd = 'ping 127.0.0.1'
        print(cmd)
        mytask = subprocess.Popen(cmd, shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            line = mytask.stdout.readline()
            # print("zkzk")
            if not line:
                break
            x = line.decode('gb2312')
            # print("%s"%x)
            # print(x)
            self.updateSig.emit(x)

class MainFrame(QDialog):  
    def __init__(self):  
        super(MainFrame,self).__init__()  
 
 
        self.terminal = QTextEdit(self)    
        
        self.myButton = QPushButton(self)  
        self.myButton.setObjectName("myButton")  
        self.myButton.setText("Test")  
        self.myButton.clicked.connect(self.startThread)  
        
        layout = QVBoxLayout()
        self.setLayout(layout)     
        layout.addWidget(self.myButton)
        layout.addWidget(self.terminal)               
    
        self.cmdThread = QTProcessThread()
        self.cmdThread.updateSig.connect(self.upDateMessage)

        #终端打印到textedit的另一种方式
    #     stdout = OutputWrapper(self,True)
    #     stdout.outputWritten.connect(self.handleOutput)
    # def handleOutput(self, text, stdout):
    #     color = self.terminal.textColor()
    #     self.terminal.setTextColor(color if stdout else self._err_color)
    #     self.terminal.moveCursor(QTextCursor.End)
    #     self.terminal.insertPlainText(text)
    #     self.terminal.setTextColor(color)

    def startThread(self):
        print ("start Thread")
        self.cmdThread.start()

    def coloredTextout(self,message):
    	print message
        if message[1:5] == "[31m":
        	self.terminal.setTextColor(QColor(255, 0, 0))
        	self.terminal.append(message[5:-5])
        elif message[1:5] == "[32m":
            self.terminal.setTextColor(QColor(0, 255, 0))
            self.terminal.append(message[5:-5])
        elif message[1:4] == "[0m":
            self.terminal.setTextColor(QColor(0, 0, 0))
            self.terminal.append(message[4:-4])
        else:
        	self.terminal.setTextColor(QColor(0, 0, 0))
        	self.terminal.insertPlainText(message)
    
    @pyqtSlot(str)
    def upDateMessage(self, message):
    	# print("sdfsfds")
    	# print(message)
        # self.terminal.append(message)
        # self.textEdit.insertPlainText(message)
        self.coloredTextout(message)


        
if __name__=="__main__":    
    qApp=QApplication(sys.argv)
    main=MainFrame()
    main.show()
    sys.exit(qApp.exec_())

