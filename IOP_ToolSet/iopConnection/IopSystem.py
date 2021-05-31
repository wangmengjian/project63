#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import rospy
from fkie_iop_msgs.msg import System, Subsystem, Identification, OcuCmd, OcuCmdEntry
import time
from threading import Thread
from ClientPool import ClientPool
import atexit
import threading

from tf_transform.tf_broadcaster import broadcaster


def callbackFunction(system):
    # print "system",system

    IopSystem.robotList = []
    for subsystem in system.subsystems:
        # print subsystem
        IopSystem.robotList.append(subsystem)

def refreshRobotList():
    rospy.Subscriber("/iop_system", System, callbackFunction)
    rospy.spin()


class IopSystem:
    robotList = []
    map = {}
    clientPool = ClientPool()

    def __init__(self):
        self.pub = rospy.Publisher('/ocu_cmd', OcuCmd, queue_size=10)
        t = Thread(target=refreshRobotList)
        t.start()

    # return robot list:Identification[]
    def showRobotList(self):
        return IopSystem.robotList

    def establishConnection(self, robot):
        if self.hasConnection(robot):
            return False
        if not self.hasRobot(robot):
            return False
        ocuMed = OcuCmd()
        # 单独定义该机器人的取消连接消息格式
        cmd = OcuCmdEntry()
        cmd.address.subsystem_id = robot.address.subsystem_id
        # cmd.address.node_id = robot.address.node_id
        # cmd.address.component_id = robot.address.component_id
        cmd.name = robot.name
        cmd.ocu_client = IopSystem.clientPool.getOcuClient(robot.address.subsystem_id)
        cmd.authority = 205
        cmd.access_control = 12
        ocuMed.cmds.append(cmd)
        IopSystem.map[robot.name] = cmd.ocu_client
        # 定义其他机器人的消息
        # for robotCycle in IopSystem.robotList:
        #     if robotCycle.address.subsystem_id != robot.address.subsystem_id:
        #         cmd = OcuCmdEntry()
        #         cmd.address.subsystem_id = robotCycle.address.subsystem_id
        #         cmd.address.node_id = robotCycle.address.node_id
        #         cmd.address.component_id = robotCycle.address.component_id
        #         cmd.name = robotCycle.name
        #         cmd.ocu_client.subsystem_id = 65535
        #         cmd.ocu_client.node_id = 0
        #         cmd.ocu_client.component_id = 0
        #         cmd.authority = 205
        #         cmd.access_control = 10
        #         ocuMed.cmds.append(cmd)
        self.pub.publish(ocuMed)
        print "zzz",ocuMed ,'kkkkkkkk'
        t1=threading.Thread(target=broadcaster, args=(robot.name,))
        t1.start()
        return True

    def hasRobot(self, robot):
        # 查询是否有该机器人
        flag = False
        for robot1 in IopSystem.robotList:
            if robot1.ident.address.subsystem_id == robot.address.subsystem_id:
                flag = True
        if not flag:
            print "没有该机器人"
            return False
        return True

    # 取消现有连接
    # 参数说明 : robot 类型为 Identification
    # return Ture/False
    def cancelConnection(self, robot):
        if not self.hasRobot(robot):
            return False
        if not robot.name in IopSystem.map.keys():
            return False
        # print "----------------------------"
        ocuMed = OcuCmd()
        # 单独定义该机器人的取消连接消息格式
        cmd = OcuCmdEntry()
        cmd.address.subsystem_id = robot.address.subsystem_id
        cmd.address.node_id = robot.address.node_id
        cmd.address.component_id = robot.address.component_id
        cmd.name = robot.name
        cmd.ocu_client = IopSystem.map[robot.name]
        cmd.authority = 205
        cmd.access_control = 10
        ocuMed.cmds.append(cmd)
        rospy.Publisher('/ocu_cmd', OcuCmd, queue_size=10).publish(ocuMed)
        IopSystem.map.pop(robot.name)
        return True

    def establishRobotsConnection(self, needRobotList):
        for needRobot in needRobotList:
            self.establishConnection(needRobot)

    def cancelRobotsConnection(self, needRobotList):
        print "cancel robotList connection"
        print needRobotList
        for needRobot in needRobotList:
            self.cancelConnection(needRobot)

    def hasConnection(self, robot):
        for connectedRobot in IopSystem.map:
            if robot == connectedRobot:
                print robot.name + " has Connected"
                return True
        return False