#!/usr/bin/env python3
import .Omniwheel_Protocol
import serial
import time
import threading
from .omniwheel_defines import *

class Communication_Management:
    def __init__(self, __comm_port = "/dev/ttyTCU0", __baudrate = 9600):

        # initialize Variables
        self.send_packet = Omniwheel_Protocol.Packet()
        self.send_packet.clearPacket()
        self.recv_list = []
        self.recv_packet = Omniwheel_Protocol.Packet()
        self.recv_packet_list = []
        # If the received packet requires debugging, enable the line below.
        # self.recv_packet.setwarnings(True)
        self.recv_packet_done = False
        self.send_packet.clearPacket()
        self.send_str_list = []

        self.prev_sent_id = 0x10
        self.prev_sent_cmd = 0xC0
        self.wait_Request_id = 0x10
        self.wait_Request_cmd = 0xC0
        self.wait_Request = False
        self.receive_packet_start = False
        self.receive_packet_done  = False

        self.comm_lock = threading.Lock()

        self.process_thr = threading.Thread(target=self.process, args=[__comm_port, __baudrate,])
        self.process_thr.setDaemon(True)
        self.process_thr.start()

    def receive_from_cortex(self, Serial_Cortex):
        while(True):
            self.receive_process(Serial_Cortex)
    def receive_process(self, Serial_Cortex):
        while Serial_Cortex.inWaiting() > 0:
            #print("1")
            data = None
            try:
                data = Serial_Cortex.read(1)
                # print("recv Data : " + str(ord(data)))
            except serial.SerialTimeoutException:
                print("timeout")
                return -1
            # print("Data : "+str(ord(data)))
            if(data is not None):
                if(len(data) > 0):
                    # if data's ASCii code equals STX.
                    if(ord(data) == 0x02):
                        self.receive_packet_start = True
                        self.receive_packet_done  = False
                        self.recv_list = [ord(data)]
                    else:
                        if(self.receive_packet_start):
                            self.recv_list.append(ord(data))
                            if(ord(data) == 0x03):
                                self.receive_packet_start = False
                                if(self.recv_packet.parsingList(self.recv_list)):
                                    if(self.wait_Request):
                                        if(self.wait_Request_id == self.recv_packet.getID()):
                                            if(self.recv_packet.getCMD() == self.wait_Request_cmd):
                                                self.wait_Request = False
                                    self.recv_packet_done = True
                                    self.recv_packet_list.append(self.recv_packet)
                                self.receive_packet_done  = True
    def is_waiting_for_response(self):
        return self.wait_Request

    def receive_available(self):
        return len(self.recv_packet_list)

    def get_recv_packet(self):
        # print("LEN : " + str(self.receive_available()))
        result = self.recv_packet_list[0]
        # print(result)
        del self.recv_packet_list[0]
        return result

    def send_to_cortex(self, id, cmd, mid, data = None):
        self.send_packet.clearPacket()
        self.send_packet.setID(id)
        self.send_packet.setCMD(cmd)

        # Refresh variables for previously sent id, cmd and mid.
        self.prev_sent_id = id
        self.prev_sent_cmd = cmd

        # If a request cmd
        if(cmd - REQUEST_DEFAULT < 10):
            self.wait_Request = True
            self.wait_Request_id = id
            self.wait_Request_cmd = cmd

        # Add payload to packet
        self.send_packet.clearPayload()
        self.send_packet.addPayload(mid, data)

        # Calculate LRC
        self.send_packet.calcLRC_Lower()

        self.comm_lock.acquire()
        self.send_str_list.append(self.send_packet.packetToList())
        self.comm_lock.release()

        # Send data to cortex using TTL.
        # send_str = self.send_packet.packetToList()

        # if(len(send_str) > 0):
        #     # print("Send Data : " + str(send_str))
        #     self.Serial_Cortex.write(send_str)
        #     # Return 1 if send success.
        #     return 1
        # # Return -1 if send failed.
        # return -1

    def send_to_cortex_list(self, id, cmd, mid_list, data_list):
        self.send_packet.clearPacket()
        self.send_packet.setID(id)
        self.send_packet.setCMD(cmd)

        # Refresh variables for previously sent id, cmd and mid.
        self.prev_sent_id = id
        self.prev_sent_cmd = cmd

        # If a request cmd
        if(cmd - REQUEST_DEFAULT < 10):
            self.wait_Request = True

        # Add payload to packet
        self.send_packet.clearPayload()
        for i in range(0, len(mid_list)):
            self.send_packet.addPayload(mid_list[i], data_list[i])

        # Calculate LRC
        self.send_packet.calcLRC()

        # Send data to cortex using TTL.
        self.comm_lock.acquire()
        self.send_str_list.append(self.send_packet.packetToList())
        self.comm_lock.release()

        # send_str = self.send_packet.packetToList()
        # if(len(send_str) > 0):
        #     self.Serial_Cortex.write(send_str)
        #     # Return 1 if send success.
        #     return 1
        # # Return -1 if send failed.
        # return -1
    def process(self, __comm_port, __baudrate):
        while(True):
            try:
                print("connect to serial...")
                # initialize Serial Port(TTL)
                Serial_Cortex = serial.Serial(
                    port = __comm_port,
                    baudrate = __baudrate,
                    # bytesize = serial.EIGHTBITS,
                    # parity = serial.PARITY_NONE,
                    # stopbits = serial.STOPBITS_ONE,
                    timeout=.1
                )
                # Wait a second to let the port initialize
                time.sleep(1)

                Serial_Cortex.write(0x03)
                Serial_Cortex.write(0x03)
                Serial_Cortex.write(0x03)
                print("done!")
                while(True):
                    try:
                        self.comm_lock.acquire()
                        res = self.receive_process(Serial_Cortex)
                        if(len(self.send_str_list) > 0):
                            send_str = self.send_str_list[0]
                            del self.send_str_list[0]
                            Serial_Cortex.write(send_str)
                            # print("send done")
                        if(res == -1):
                            print("time out!")
                            break
                        self.comm_lock.release()
                    except Exception as e:
                        Serial_Cortex.close()
                        print(e)
                        break
                    time.sleep(0.01)
            except Exception as e:
                print(e)
                break

if __name__ == "__main__":
    comm = Communication_Management()
    prev_send_time=time.time()
    a = 0
    while(True):
        try:
            if(time.time() - prev_send_time > 0.5):
                prev_send_time=time.time()
                if(a % 2 == 0):
                    comm.send_to_cortex(CORTEX_ID, REQUEST_ODOMETER, MID_WHEEL_1)
                else:
                    comm.send_to_cortex(CORTEX_ID, CONTROL_ENCODER, MID_WHEEL_1)
                a += 1
            if(comm.receive_available() > 0):
                p = comm.get_recv_packet()
                print(p.packetToList())
                if(p.getID() == CORTEX_ID):
                    if(p.getCMD() == (REQUEST_ODOMETER+ANSWER_REQUEST_CONST)):
                        payload = p.getPayload()
                        for pay in payload:
                            print("\nMID : " + str(pay.getID()))
                            if(pay.getID() == MID_WHEEL_1):
                                print("Data : " + str(pay.getData()))
                            elif(pay.getID() == MID_WHEEL_2):
                                print("Data : " + str(pay.getData()))
                            elif(pay.getID() == MID_WHEEL_3):
                                print("Data : " + str(pay.getData()))
            time.sleep(0.02)
        except Exception as e:
            print(e)
            break
