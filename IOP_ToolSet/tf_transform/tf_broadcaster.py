#!/usr/bin/env python
#coding=utf-8

import rospy

import tf
import nav_msgs.msg
from threading import Thread
import geometry_msgs.msg._PointStamped


def handle_robot_pose(msg, robotname):
    # print "---------------"
    br = tf.TransformBroadcaster() #将坐标变换广播出去
    br.sendTransform((msg.pose.pose.position.x, msg.pose.pose.position.y, 0),  # 平移
                     (msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z,
                      msg.pose.pose.orientation.w),  # 旋转  quaternion_from_euler:欧拉角变四元数
                     rospy.Time.now(),  # 打上时间戳
                     '/%s/client_odom' % robotname,  # 发布 robotname 到 "map" 的平移和翻转
                     "world")
def broadcaster(robotname):
    print '广播机器人'+robotname+"坐标"
    rospy.Subscriber('/%s/client_odom' % robotname, #要接收的topic名  /turtle1/pose或者/turtle2/pose
                     nav_msgs.msg.Odometry,  #接收的数据类型
                     handle_robot_pose,      #回调函数
                     robotname)              #回调函数参数
    rospy.spin() #保持节点运行，直到节点关闭
if __name__=='__main__':
    rospy.init_node("sdfsdf")
    broadcaster("bulldog")