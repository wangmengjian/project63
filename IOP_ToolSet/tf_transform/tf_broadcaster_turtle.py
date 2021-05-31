#!/usr/bin/env python
#coding=utf-8

import rospy

import tf
import nav_msgs.msg
from threading import Thread
import turtlesim.msg


def handle_robot_pose(msg):
    # print "---------------"
    br = tf.TransformBroadcaster() #将坐标变换广播出去
    #向/tf发布消息
                      #robot距离原点的坐标
    br.sendTransform((msg.x, msg.y, 0), #平移
                     (0, 0, 0, 0), #旋转  quaternion_from_euler:欧拉角变四元数
                     rospy.Time.now(), #打上时间戳
                     '/turtle1/odom',  #发布 robotname 到 "map" 的平移和翻转
                     "world")

def broadcaster():
    print "广播turtle坐标"
    rospy.Subscriber('/turtle1/pose', #要接收的topic名  /turtle1/pose或者/turtle2/pose
                     turtlesim.msg.Pose,  #接收的数据类型
                     handle_robot_pose)
    rospy.spin() #保持节点运行，直到节点关闭
if __name__=='__main__':
    rospy.init_node("sdfsdf")
    broadcaster()