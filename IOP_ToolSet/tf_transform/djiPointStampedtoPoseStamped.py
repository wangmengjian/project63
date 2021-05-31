#!/usr/bin/env python
#coding=utf-8

import rospy

import tf
import nav_msgs.msg
from threading import Thread
import geometry_msgs.msg._PointStamped

pub=rospy.Publisher("/dji_sdk/local_positon")
def feedback(msg):
    print '更改无人机坐标to poseStamped'


def changeCoordinate():
    rospy.Subscriber('/dji_sdk/local_position', #要接收的topic名  /turtle1/pose或者/turtle2/pose
                     nav_msgs.msg.Odometry,  #接收的数据类型
                     feedback,      #回调函数
                     )              #回调函数参数
    rospy.spin() #保持节点运行，直到节点关闭
if __name__=='__main__':
    rospy.init_node("sdfsdf")
    broadcaster("bulldog")