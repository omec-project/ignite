#!/bin/bash
#
# Copyright 2019, Infosys Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

cp /opt/ignite/Dev/Common/shared/configuration.json /opt/ignite/Dev/Common/configuration.json
cp /opt/ignite/Dev/Common/shared/resources.MMEConfig.txt /opt/ignite/Test/ROBOTCs/resources/resources.MMEConfig.txt

APPLICATION=$1

case $APPLICATION in
    "diameter")
      echo "Starting diameter proxy"
	  cd /opt/ignite/Dev/Protocols/Diameter/
      python3 diameterProxy.py
      ;;
    "s1ap")
      echo "Starting s1ap proxy"
	  cd /opt/ignite/Dev/Protocols/S1AP/
      python3 s1apProxy.py
      ;;
    "gtp")
      echo "Starting gtp proxy"
	  cd /opt/ignite/Dev/Protocols/GTP/
      python3 udpProxy.py
      ;;
    *)
      echo "invalid app $APPLICATION"
      ;;
esac
