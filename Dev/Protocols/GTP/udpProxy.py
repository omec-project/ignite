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
import threading
from flask import Flask, request, Blueprint

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Common'))
from genericProxy import GenericProxy
from genericProxy import app_send
from genericProxy import app_receive
from genericProxy import ctx_data
from genericProxy import clear_buffer

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Logger'))
import igniteLogger

configuration_file = os.path.join(os.path.dirname(__file__), '..','..','Common','configuration.json')
with open(configuration_file) as configuration:
        config_file=json.loads(configuration.read())


app = Flask(__name__)

######send
app.register_blueprint(app_send)

#####receive
app.register_blueprint(app_receive)

#ctx_data
app.register_blueprint(ctx_data)

#clearbuffer
app.register_blueprint(clear_buffer)

def udpProxyStart():
    udp_proxy = GenericProxy("gtp")
    igniteLogger.logger.info("GTP Proxy created")
    udp_proxy.create_sut_socket()
    igniteLogger.logger.info("GTP SUT socket created")
    udp_proxy.runProxy()


def runner():
    app.run(config_file["gtp"]["ignite_ip"], config_file["gtp"]["tc_port"])


gtp_thread = threading.Thread(target=udpProxyStart)
gtp_runner = threading.Thread(target=runner)
gtp_runner.start()
gtp_thread.start()
