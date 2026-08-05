# -*- coding: utf-8 -*-
"""
Created on Thu May 14 16:39:33 2020

@author: Troniya
"""
from .Payload import *


class Packet:
    def __init__(self, maxPayloadListLen=10, maxPacketByteLen=200):
        """
        STX : 프로토콜의 시작을 알리는 바이트 데이터
        ETX : 프로토콜의 끝을 알리는 바이트 데이터
        """
        self.stx = 0x02
        self.etx = 0x03

        """
        p_Enable : 현재 패킷이 유효한 상태인지 확인
        p_ID : 현재 패킷의 ID
        p_CMD : 현재 패킷의 데이터 형태( Default : 0xA0 = 요청 0xB0 = 응답 0xC0 = 제어 )
        p_Length : 현재 패킷의 CMD부터 Payload까지의 Ascii 리스트의 길이
        p_PayloadList : 실제 데이터, 명령이 들어가는 Payload가 저장되는 리스트
        p_LRC : 패킷의 유효성을 검사할 수 있는 LRC 데이터
        """
        self.p_Enable = False
        self.p_ID = None
        self.p_CMD = None
        self.p_Length = 0
        self.p_PayloadList = []
        self.p_Payload_MID_List = []
        self.p_LRC = None

        """
        ID_Set_State : 현재 패킷의 ID가 설정되었는지 확인
        CMD_Set_State : 현재 패킷의 CMD가 설정되었는지 확인
        LRC_Check : 현재 패킷의 LRC가 체크되었는지 확인
        warningFlag : 클래스의 함수들을 진행하며 문제가 발생했거나 문제될 여지가 있는 경우 워닝을 발생시키는 변수 (True : 발생 , False : 발생하지 않음)
        """
        self.ID_Set_State = False
        self.CMD_Set_State = False
        self.LRC_Check = False
        self.warningFlag = False

        """
        Packet Payload 최대 갯수 설정
        Packet 바이트 변환시 최대 길이 제한
        """
        self.maxPayloadListLen = maxPayloadListLen
        self.maxPacketByteLen = maxPacketByteLen

    def clearPacket(self):
        self.stx = 0x02
        self.etx = 0x03

        self.p_Enable = False
        self.p_ID = None
        self.p_CMD = None
        self.p_Length = 0
        self.p_PayloadList = []
        self.p_LRC = None

        self.ID_Set_State = False
        self.CMD_Set_State = False
        self.LRC_Check = False

    def setwarnings(self, ena):
        self.warningFlag = ena

    def getwarnings(self):
        return self.warningFlag

    def setSTX(self, stx):
        if (self.warningFlag):
            raise Warning(
                "This Function can cause fatal problems in communications.\nIf this function is required, this warning can be ignored by using \"setwarnings(False)\".")

        if (self.checkNumToByte(stx)):
            self.LRC_Check = False
            self.stx = stx

    def setETX(self, etx):
        if (self.warningFlag):
            raise Warning(
                "This Function can cause fatal problems in communications.\nIf this function is required, this warning can be ignored by using \"setwarnings(False)\".")

        if (self.checkNumToByte(etx)):
            self.LRC_Check = False
            self.etx = etx

    def checkNumToByte(self, data):
        if (data > 0xFF):
            if (self.warningFlag):
                raise Warning("it is Greater than Maximum Number.")
            return False
        if (data < 0x00):
            if (self.warningFlag):
                raise Warning("it is Less than Minimum Number.")
            return False
        return True

    def setID(self, _ID):
        if (self.checkNumToByte(_ID)):
            self.LRC_Check = False
            self.p_ID = _ID
            self.ID_Set_State = True

    def setCMD(self, _CMD):
        if (self.checkNumToByte(_CMD)):
            self.LRC_Check = False
            self.p_CMD = _CMD
            self.CMD_Set_State = True

    def clearPayload(self):
        self.p_PayloadList.clear()
        self.p_Payload_MID_List = []
        if (self.CMD_Set_State):
            self.p_Length = 1
        else:
            self.p_Length = 0
        self.LRC_Check = False

    def addPayload(self, mid, data=None):
        if (self.checkNumToByte(mid)):
            self.LRC_Check = False
            if(mid not in self.p_Payload_MID_List):
                p = payload()
                p.setData(mid, data)
                if (p.available()):
                    if (len(self.p_PayloadList) < self.maxPayloadListLen):
                        self.p_Payload_MID_List.append(mid)
                        self.p_PayloadList.append(p)
                        self.p_Length += p.getLength()
            else:
                self.p_PayloadList[self.p_Payload_MID_List.index(mid)].setData(mid, data)

            if(self.warningFlag):
                raise Exception("mid data is not within range")

    def removePayload(self, index):
        del self.p_PayloadList[index]
        del self.p_Payload_MID_List[index]
        self.LRC_Check = False

    def calcLRC(self):
        if (self.CMD_Set_State):
            s = self.p_CMD
        else:
            if (self.warningFlag):
                raise Warning("LRC Check Error!\nCMD has not been set.")
            s = 0
        if (len(self.p_PayloadList) != 0):
            s += sum(self.getPayloadAsciiArray())

        result_not = ~s + 1
        result = hex(result_not & 0xFF)
        if (len(result) < 3):
            if (self.warningFlag):
                raise Warning("LRC Check Error!\n\"hex\" Function is not working")
            return
        elif (len(result) < 4):
            str_result = "0" + result[-1]
        elif (len(result) == 4):
            str_result = result[-2:]
        else:
            if (self.warningFlag):
                raise Warning("LRC Check Error!\ncheck the calcLRC's bit logic operation.")
            return
        self.p_LRC = str_result
        self.LRC_Check = True

    def calcLRC_Lower(self):
        if (self.CMD_Set_State):
            s = self.p_CMD
        else:
            if (self.warningFlag):
                raise Warning("LRC Check Error!\nCMD has not been set.")
            s = 0
        if (len(self.p_PayloadList) != 0):
            s += sum(self.getPayloadAsciiArray())

        result_not = ~s + 1
        result = hex(result_not & 0xFF)
        if (len(result) < 3):
            if (self.warningFlag):
                raise Warning("LRC Check Error!\n\"hex\" Function is not working")
            return
        elif (len(result) < 4):
            str_result = "0" + result[-1]
        elif (len(result) == 4):
            str_result = result[-2:]
        else:
            if (self.warningFlag):
                raise Warning("LRC Check Error!\ncheck the calcLRC's bit logic operation.")
            return
        str_result = str_result.upper()
        self.p_LRC = str_result
        self.LRC_Check = True

    def calcLength(self):
        if (self.CMD_Set_State):
            s = 1
            for payload in self.p_PayloadList:
                s += payload.getLength()
            self.p_Length = s
            if (self.p_Length > 99):
                return False
            return True
        else:
            if (self.warningFlag):
                raise Warning("Packet Length Check Error!\nCMD has not been set.")
            return False

    def getSTX(self):
        return self.stx

    def getETX(self):
        return self.etx

    def getID(self):
        return self.p_ID

    def getLength(self):
        return self.p_Length

    def getCMD(self):
        return self.p_CMD

    def getPayloadLength(self):
        return len(self.p_PayloadList)

    def getPayload(self, index=None):
        if (index == None):
            return self.p_PayloadList
        elif (str(type(index)) == "<class 'int'>"):
            if ((index >= 0) and (index < self.getPayloadLength())):
                return self.p_PayloadList[index]
            else:
                if (self.warningFlag):
                    raise Warning("Index Error!\nindex " + str(index) + " is out of Range")
                return None

    def getLRC(self):
        return self.p_LRC

    def getPayloadAsciiArray(self):
        bytelist = []
        for payload in self.p_PayloadList:
            bytelist += payload.getAsciiArray()
        return bytelist

    def packetToList(self):
        packetByteList = []
        if (self.LRC_Check):
            if (self.calcLength()):
                packetByteList.append(self.stx)
                packetByteList.append(self.p_ID)
                packetByteList.append(ord(str(int(self.p_Length / 10))))
                packetByteList.append(ord(str(int(self.p_Length % 10))))
                packetByteList.append(self.p_CMD)
                packetByteList += self.getPayloadAsciiArray()
                packetByteList += [int(ord(i)) for i in self.p_LRC]
                packetByteList.append(self.etx)
                return packetByteList
        else:
            if (self.warningFlag):
                raise Warning("Packet Length Check Error!\nLRC is not Checked")
            return packetByteList

    def listPayloadParse(self, l):
        nl = [x for x in l if 0x80 <= x <= 0x8F]
        startIndex = 0
        t = []
        for x in nl:
            t.append(l[startIndex:l.index(x)])
            startIndex = l.index(x)
        t.append(l[startIndex:-1])
        return t

    def big2Small(self, _str):
        return _str.lower()

    """
    parsingList :
        Ascii List를 파싱하여 패킷에 저장한다.
    """

    def parsingList(self, l):
        if (l[0] == 0x02 and l[-1] == 0x03):
            self.setID(l[1])
            self.setCMD(l[4])
            self.clearPayload()
            p_lists = self.listPayloadParse(l[5:-2])
            p_lists = [x for x in p_lists if x]
            # print(p_lists)
            for p_list in p_lists:
                p = payload()
                if (p.listToPayload(p_list)):
                    self.p_PayloadList.append(p)
                    self.p_Length += p.getLength()
                    # print(p.getID())
                    # print(p.getData())

            self.calcLRC()
            if ((self.big2Small(self.p_LRC) != self.big2Small((chr(l[-3]) + chr(l[-2]))))):
                if (self.warningFlag):
                    raise Exception("LRC Error!\ngot " + (chr(l[-3]) + chr(l[-2])) + ", need " + self.p_LRC)
                print("LRC Error!\ngot " + (chr(l[-3]) + chr(l[-2])) + ", need " + self.p_LRC)
                self.clearPacket()
                return False
            else:
                return True
        else:
            if (self.warningFlag):
                raise Warning("List is not start with STX or is not end with ETX!Check the Received Ascii List")
            return False

if __name__ == "__main__":
    p = Packet()
    list_ = [0x02, 0x10, 0x32, 0x31, 0xC1, 0x80, 0x30, 0x30, 0x30, 0x30, 0x81, 0x30, 0x30, 0x30, 0x30, 0x82, 0x30, 0x30,
             0x30, 0x30, 0x83, 0x30, 0x30, 0x30, 0x30, 0x33, 0x39, 0x03]
    p.parsingList(list_)
