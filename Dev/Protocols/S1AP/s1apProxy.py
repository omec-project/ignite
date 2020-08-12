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

import os
import sys
import requests
import json
import time
import threading
import s1apTC as s1
from flask import Flask, request, Blueprint

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Common'))
from genericProxy import GenericProxy
from genericProxy import app_send
from genericProxy import app_receive
from genericProxy import ctx_data
from genericProxy import clear_buffer

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Logger'))
import igniteLogger

# currentDir = os.path.dirname(__file__)
configuration_file = os.path.join(os.path.dirname(__file__), '..', '..', 'Common', 'configuration.json')
with open(configuration_file) as configuration:
    config_file = json.loads(configuration.read())

app = Flask(__name__)

######send
app.register_blueprint(app_send)

#####receive
app.register_blueprint(app_receive)

# ctxdata
app.register_blueprint(ctx_data)

# clearbuffer
app.register_blueprint(clear_buffer)


def s1apProxyStart(enodeBType):
    if enodeBType=="source":
        s1ap_proxy=GenericProxy("s1ap")
        igniteLogger.logger.info("S1ap Proxy created")
        s1ap_proxy.create_sut_socket()
        igniteLogger.logger.info("S1ap SUT socket created")
        s1ap_proxy.runProxy()

    elif enodeBType == "target":
        s1aptarget_proxy=GenericProxy("s1ap_target")
        igniteLogger.logger.info("S1ap Target Proxy created")
        s1aptarget_proxy.create_sut_socket()
        igniteLogger.logger.info("S1ap Target SUT socket created")
        s1aptarget_proxy.runProxy()

def runner(enodeBType):
    if enodeBType=="source":
        app.run(config_file["s1ap"]["ignite_ip"],config_file["s1ap"]["tc_port"])
    elif enodeBType=="target":
        app.run(config_file["s1ap_target"]["ignite_ip"], config_file["s1ap_target"]["tc_port"])



s1apArg = sys.argv
s1ap_thread= threading.Thread(target=s1apProxyStart,args=(s1apArg[1],))
s1ap_runner= threading.Thread(target=runner, args=(s1apArg[1],))
s1ap_runner.start()
s1ap_thread.start()

time.sleep(3)

if s1apArg[1] == "source":
    s1_setup_request = json.loads(open('../../../Test/MessageTemplates/S1AP/s1setup_request.json').read())
    print("send S1 set up")
    igniteLogger.logger.info("\n-------------------------------\nsend source s1 set up\n----------------------")
    igniteLogger.logger.info("\n---------------------------------------\nSend S1Setup Request to MME\n---------------------------------------")
    s1.sendS1ap('s1_setup_request',s1_setup_request,None)
    igniteLogger.logger.info("\n---------------------------------------\nS1 Setup Response received from MME\n---------------------------------------")
    s1.receiveS1ap()


elif s1apArg[1] == "target":
    s1_setup_request = json.loads(open('../../../Test/MessageTemplates/S1AP/s1setup_request_target.json').read())
    print("s1 set up target")
    igniteLogger.logger.info("\n-------------------------------\nsend target s1 set up\n----------------------")
    igniteLogger.logger.info("\n---------------------------------------\nSend S1Setup Request to MME\n---------------------------------------")
    s1.sendS1ap('s1_setup_request_target',s1_setup_request,None)
    igniteLogger.logger.info("\n---------------------------------------\nS1 Setup Response received from MME\n---------------------------------------")
    s1.receiveS1ap(target=True)

print ("\n-------------------------------------\nSetup Successful\n---------------------------------------")
















