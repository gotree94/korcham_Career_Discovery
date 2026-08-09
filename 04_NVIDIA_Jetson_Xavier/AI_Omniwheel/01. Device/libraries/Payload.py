# -*- coding: utf-8 -*-
"""
Created on Thu May 6 15:06:08 2021

@author: Troniya
"""


class payload:
    def __init__(self):
        self.isEmpty = True
        self.mid = None
        self.data = None
        self.data_Enable = False

    def setData(self, _mid, _data=None):
        self.mid = _mid
        #        print(self.mid)
        if _mid is not None:
            self.isEmpty = False
        else:
            self.isEmpty = True

        if _data is not None:
            self.data = _data
            self.data_Enable = True
        else:
            self.data = None
            self.data_Enable = False

    def available(self):
        return not self.isEmpty

    def getAsciiArray(self, toInt=False):
        if self.isEmpty is not True:
            result_list = [self.mid]
            if (self.data_Enable):
                result_list += [int(ord(i)) for i in str(self.data)]
            return result_list

    def clear(self):
        self.mid = None
        self.data = None
        self.data_Enable = False
        self.isEmpty = True

    def dataAvailable(self):
        return self.data_Enable

    def getData(self):
        if self.isEmpty:
            raise Exception("Payload is Now Empty...Try to setData")
        else:
            if self.data_Enable is not True:
                raise Exception(
                    "Payload's Data is not Available...\nTry to check before received data line or Try to check the \"setData\" Function.")
            else:
                return self.data

    def getID(self):
        if self.isEmpty:
            raise Exception("Payload is Now Empty...Try to setData")
        else:
            return self.mid

    def getLength(self):
        if self.isEmpty:
            raise Exception("Payload is Now Empty...Try to setData")
        else:
            if self.data_Enable is not True:
                return 1
            else:
                return 1 + len(str(self.data))

    def ascii2Str(self, dataList):
        return ''.join(map(chr, dataList))

    def listToPayload(self, p_list):
        if (len(p_list) > 0):
            if (p_list[0] >= 0x80 and p_list[0] <= 0x8F):
                if (len(p_list) > 1):
                    self.setData(p_list[0], self.ascii2Str(p_list[1:]))
                else:
                    self.setData(p_list[0])
                return True
            else:
                return False
        #                raise Exception("Payload list is not start with 0x80 ~ 0x8F")
        else:
            return False
#            raise Exception("Payload list is Empty")
