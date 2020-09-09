#
# Copyright (c) 2019, Infosys Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from flask import Flask, escape, request,json,jsonify,Blueprint
import socket
import select
from binascii import hexlify
from time import sleep
import os
import sys
import json
import requests
import time, datetime

#logger imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Logger'))
import igniteLogger

#s1ap imports
import sctp
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Protocols', 'S1AP'))
import s1apEncoder
import s1apDecoder
from s1apGrammar import *

#diameter imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Protocols', 'Diameter'))
import diameterEncoder
import diameterDecoder
import diameterUtils as du
import igniteCommonUtil

#gtp imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Protocols', 'GTP'))
import gtpEncoder
import gtpDecoder
from gtpGrammar import workbook
import re

currentDir = os.path.dirname(__file__)
configFile = os.path.join(currentDir, 'configuration.json')
with open(configFile) as configuration:
            config_file=json.loads(configuration.read())
output = []
outFlag=False
PROTOCOLMESSAGE={}
CTXDATA={}
UEID=""

clear_buffer= Blueprint('clear_buffer', __name__)
@clear_buffer.route('/clearMessageBuffer', methods = ['GET'])
def clearMessageBuffer():
    global outFlag
    global output
    output=[]
    outFlag=False
    igniteLogger.logger.info(f"outFlag : {outFlag}")
    return {"status":"Ok"}

ctx_data= Blueprint('ctx_data', __name__)
@ctx_data.route('/getContextData', methods = ['GET'])
def getContextData():
    global CTXDATA
    return CTXDATA

app_send = Blueprint('app_send', __name__)
@app_send.route('/sendMessagesToProxy', methods = ['POST'])
def sendMessagesToProxy():
    global PROTOCOLMESSAGE
    global CTXDATA
    global UEID

    if request.is_json:
        data=request.get_json()
    for key in data[1].keys():
        CTXDATA[key]=data[1][key]
    
    if len(data) > 3 and data[2] == 's1ap' and data[3] != None:
        UEID=str(data[3])
        
    igniteLogger.logger.info("tc data of "f"{data[2]} : "f"{data[0]}")
    igniteLogger.logger.info("context data of "f"{data[2]} : "f"{CTXDATA}")
    PROTOCOLMESSAGE=data[0]
    return PROTOCOLMESSAGE

app_receive = Blueprint('app_receive', __name__)
@app_receive.route('/getMessagesfromProxy', methods = ['GET'])
def getMessagesfromProxy():
    global output
    global outFlag
    current_time=datetime.datetime.now()+datetime.timedelta(0,9)
    while datetime.datetime.now() < current_time:
        if outFlag:
            data=output[0]
            output.pop(0)
            if len(output)<1:
                outFlag=False
            return data

def loadGTPIETypeGrammerData():
    global ieLocation
    sheet = workbook.sheet_by_index(2)
    rows = sheet.nrows
    cols = sheet.ncols
    reg_ex1 = "Type\s*=\s*(\d+)\s*\((.*)\)"
    reg_ex3 = "IE Definition End\s*:(.*)"
    ieLocation={}
    ie=0
    for row in range(rows):
        for col in range(cols):
            cell = sheet.cell(row, col)
            match = re.search(reg_ex1,str(cell.value))
            match1 = re.search(reg_ex3,str(cell.value))
            if match:
                msg_ie_type=int(match.group(1))
                if msg_ie_type not in ieLocation:
                    ieLocation[msg_ie_type] = {}
                ie_loc=ieLocation[msg_ie_type]
                ie_loc.update({"lrow":int(row)+3,"lcol":int(col),"hcol":int(col)+8})
            if match1:
                ie_loc.update({"hrow":int(row)})
    return ieLocation


class GenericProxy:
    def __init__(self,type_of_proxy):
        #method loading the values in configuration file
        result = self.loadConfigurationData(configFile)
        self.ieLocation=loadGTPIETypeGrammerData()

        if (type_of_proxy in result.keys()):
            self.type_of_proxy=type_of_proxy
            self.type_of_socket = result[type_of_proxy]["type_of_socket"]
            self.sut_ip = result[type_of_proxy]["sut_ip"]
            self.sut_port = result[type_of_proxy]["sut_port"]
            self.ignite_ip = result[type_of_proxy]["ignite_ip"]
            self.ignite_port = result[type_of_proxy]["ignite_port"]
            self.sut_socket=1

        else:
            igniteLogger.logger.error("Invalid Proxy")
            return


    def loadConfigurationData(self, configuration_file):
        with open(configuration_file) as config_file:
           config_data = json.loads(config_file.read())
        return config_data

    def create_sut_socket(self):
        # Socket setup for connecting to SUT
        if(self.type_of_proxy=="gtp"):
             self.sut_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        elif(self.type_of_proxy == "diameter" or  self.type_of_proxy.startswith("s1ap")):
             socket.IPPROTO_SCTP = 132
             self.sut_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM,socket.IPPROTO_SCTP)

        self.sut_socket.bind((self.ignite_ip, self.ignite_port))

        if(self.type_of_proxy.startswith("s1ap")):
             self.sut_socket.connect((self.sut_ip,self.sut_port))

        elif(self.type_of_proxy=="diameter"):
             self.sut_socket.listen(1)
             self.sut_socket.setblocking(0)

        igniteLogger.logger.info("Socket to SUT binded to IP : "f"{self.ignite_ip}, Port : ,"f"{self.sut_port}")

    def sendDiamDataToSut(self,sut_diam_conn_socket, msg_data):
        length, e_data = diameterEncoder.encodeDiameter(msg_data["diameter"]["msg"])
        sut_diam_conn_socket.send(e_data[0:length])

    def runProxy(self):
        size=5120
        running_inputList = [self.sut_socket]
        running_outputList = []
        global output
        global outFlag
        global PROTOCOLMESSAGE
        global CTXDATA
        global UEID

        sut_address=(self.sut_ip, self.sut_port)

        running = 1
        sut_diam_conn_socket = 1

        while running:
            try:
                if PROTOCOLMESSAGE:
                    if self.type_of_proxy == "diameter":
                        igniteLogger.logger.info("Diameter data from Test-Case being sent to SUT : "f"{PROTOCOLMESSAGE}")
                        # Encode the message
                        length, e_data = diameterEncoder.encodeDiameter(PROTOCOLMESSAGE["diameter"]["msg"])
                        PROTOCOLMESSAGE=None
                        igniteLogger.logger.info("Encoded Diameter data: "f"{e_data[0:length]}")
                        sut_diam_conn_socket.send(e_data[0:length])

                    elif self.type_of_proxy == "gtp":
                        # Encode the message
                        igniteLogger.logger.info("GTP data from Test-Case being sent to SUT : "f"{PROTOCOLMESSAGE}")
                        e_data, length = gtpEncoder.encodeGTP(PROTOCOLMESSAGE["gtpv2"]["msg"],ieLocation)
                        PROTOCOLMESSAGE = None
                        igniteLogger.logger.info("Encoded GTP data: "f"{e_data[0:length]}")
                        self.sut_socket.sendto(e_data[0:length], sut_address)

                    elif self.type_of_proxy.startswith("s1ap"):
                                                # Encode the message
                        igniteLogger.logger.info("S1AP data from Test-Case being sent to SUT : "f"{PROTOCOLMESSAGE}")
                        nas_data = PROTOCOLMESSAGE["NAS-MESSAGE"]
                        if UEID != "" :
                            e_data = s1apEncoder.s1apEncoding(PROTOCOLMESSAGE,asn1_obj_encoder,nas_data, CTXDATA[UEID])
                        else :
                            e_data = s1apEncoder.s1apEncoding(PROTOCOLMESSAGE,asn1_obj_encoder,nas_data)

                        UEID = ""
                        PROTOCOLMESSAGE = None
                        e_byte = bytearray.fromhex(e_data)
                        igniteLogger.logger.info("Encoded S1AP data: "f"{e_byte}")
                        self.sut_socket.send(e_byte)


                input_ready,output_ready,except_ready=select.select(running_inputList,running_outputList,[],0.0005)
                if input_ready:
                    print("input ready:",input_ready)
                    for sock in input_ready:
                        if sock == self.sut_socket:
                            if self.type_of_proxy == "diameter":
                                print(self.sut_socket)
                                sut_diam_conn_socket,sut_address = self.sut_socket.accept()
                                sut_diam_conn_socket.setblocking(0)
                                running_inputList.append(sut_diam_conn_socket)

                            elif (self.type_of_proxy == "gtp") or (self.type_of_proxy.startswith("s1ap")):
                                sut_data = self.sut_socket.recv(size)
                                if sut_data:
                                    if self.type_of_proxy.startswith("s1ap"):
                                        igniteLogger.logger.info("S1AP Data from SUT to Test-Case: "f"{hexlify(sut_data).decode('utf-8')}")
                                        decoded_msg = s1apDecoder.Decoding(hexlify(sut_data).decode("utf-8"),asn1_obj_decoder)
                                        msg = list(decoded_msg)
                                        decoded_msg = {}
                                        decoded_msg['S1AP-PDU'] = msg
                                        igniteLogger.logger.info("Decoded S1AP data: "f"{decoded_msg}")

                                    elif self.type_of_proxy == "gtp" :
                                        igniteLogger.logger.info("GTP Data from SUT to Test-Case: "f"{hexlify(sut_data).decode('utf-8')}")
                                        decoded_msg, length = gtpDecoder.decodeGTP(sut_data,self.ieLocation)
                                        igniteLogger.logger.info("Decoded GTP data: "f"{decoded_msg}")

                                    msg_buf = json.dumps(decoded_msg)
                                    output.append(msg_buf)
                                    outFlag=True

                        elif sock==sut_diam_conn_socket:
                            data = sut_diam_conn_socket.recv(size)
                            if data:
                                length, msg = diameterDecoder.decodeDiameter(data)
                                if du.get(msg,"diameter","command-code")==257:
                                    igniteLogger.logger.info("Received CER Diameter Packet with command-code : 257")
                                    igniteLogger.logger.info("The data from diamSocket : "f"{hexlify(data)}")
                                    igniteLogger.logger.info(f"The data to diamSocket : f{msg}")
                                    igniteLogger.logger.info("Send CEA Diameter Packet with command-code: 257")
                                    msg_heirarchy, msg_data = igniteCommonUtil.loadMessageData("../../../Test/MessageTemplates/Diameter/cea.json")
                                    origin_state_id = du.get(msg,"diameter","origin-state-id")
                                    hbh = du.get(msg,"diameter","hop-by-hop-identifier")
                                    ete = du.get(msg,"diameter","end-to-end-identifier")
                                    msg_data = du.replace(msg_data,"diameter","hop-by-hop-identifier",hbh)
                                    msg_data = du.replace(msg_data,"diameter","end-to-end-identifier",ete)
                                    msg_data = du.replace(msg_data,"diameter","origin-state-id",origin_state_id)
                                    msg_data = du.replace(msg_data,"diameter","host-ip-address",self.ignite_ip)
                                    msg_data = du.replace(msg_data,"diameter","origin-host",config_file["diameter"]["ignite_host"])
                                    msg_data = du.replace(msg_data,"diameter","origin-realm",config_file["diameter"]["ignite_realm"])
                                    igniteLogger.logger.info("The msg_data : "f"{msg_data}")
                                    self.sendDiamDataToSut(sut_diam_conn_socket, msg_data)

                                elif du.get(msg,"diameter","command-code")==280:
                                    igniteLogger.logger.info("Received CER Diameter Packet with command-code : 280")
                                    igniteLogger.logger.info("The data from diamSocket : "f"{hexlify(data)}")
                                    igniteLogger.logger.info(f"The data to diamSocket : f{msg}")
                                    igniteLogger.logger.info("Send CEA Diameter Packet with command-code: 280")
                                    msg_heirarchy, msg_data = igniteCommonUtil.loadMessageData("../../../Test/MessageTemplates/Diameter/dwa.json")
                                    hbh = du.get(msg,"diameter","hop-by-hop-identifier")
                                    ete = du.get(msg,"diameter","end-to-end-identifier")
                                    msg_data = du.replace(msg_data,"diameter","hop-by-hop-identifier",hbh)
                                    msg_data = du.replace(msg_data,"diameter","end-to-end-identifier",ete)
                                    msg_data = du.replace(msg_data,"diameter","origin-host",config_file["diameter"]["ignite_host"])
                                    msg_data = du.replace(msg_data,"diameter","origin-realm",config_file["diameter"]["ignite_realm"])
                                    igniteLogger.logger.info("The msg_data : "f"{msg_data}")
                                    self.sendDiamDataToSut(sut_diam_conn_socket, msg_data)

                                else :
                                    igniteLogger.logger.info("Diameter Data from SUT sent to Test-Case: "f"{hexlify(data)}")
                                    length, decoded_msg = diameterDecoder.decodeDiameter(igniteCommonUtil.convertBytesToIntArray(hexlify(data)))
                                    data =None
                                    igniteLogger.logger.info("Decoded Diameter Data: "f"{decoded_msg}")
                                    msg_buf = json.dumps(decoded_msg)
                                    output.append(msg_buf)
                                    outFlag=True

                else:
                    continue

            except Exception as e:
                if PROTOCOLMESSAGE != None:
                    PROTOCOLMESSAGE=None
                if sut_diam_conn_socket in running_inputList:
                    running_inputList.remove(sut_diam_conn_socket)
                    sut_diam_conn_socket.close()
                igniteLogger.logger.info("Printing exception : "f"{e}")

				
            except KeyboardInterrupt:
                igniteLogger.logger.error("keyboard interrupt, closing Sockets")
                self.sut_socket.close()
            except:
                continue
