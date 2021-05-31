#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import rospy
from fkie_iop_msgs.msg import System, Subsystem, Identification, OcuCmd, OcuCmdEntry, JausAddress
import time
from threading import Thread


class ClientPool:
    # ocuClients = []
    # maxSize = 5
    #
    # def __init__(self):
    #     for i in range(1, ClientPool.maxSize + 1):
    #         client = JausAddress()
    #         client.subsystem_id = 153
    #         client.node_id = 60 + i
    #         client.component_id = 200
    #         ClientPool.ocuClients.append(client)

    def getOcuClient(self,subsystem_id):
        client = JausAddress()
        client.subsystem_id = 153
        client.node_id = 60 + subsystem_id
        client.component_id = 200
        # client.component_id = 0
        return client
    #
    # def returnOcuClient(self, ocu_client):
    #     if self.isFull():
    #         return False
    #     else:
    #         ClientPool.ocuClients.append(ocu_client)
    #         return True
    #
    # def isEmpty(self):
    #     if len(ClientPool.ocuClients) <= 0:
    #         print "无多余的ocu客户端"
    #         return True
    #     else:
    #         return False
    #
    # def isFull(self):
    #     if len(ClientPool.ocuClients) >= ClientPool.maxSize:
    #         print "ocu客户端已满"
    #         return True
    #     else :
    #         return False

