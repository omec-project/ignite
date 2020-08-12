#!/bin/sh
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

set -ex

cp /opt/ignite/Dev/Common/config/configuration.json /opt/ignite/Dev/Common/shared/configuration.json
cd /opt/ignite/Dev/Common/shared

MME_IP=$(curl -ks -X GET  -H "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)"  https://$KUBERNETES_SERVICE_HOST/api/v1/namespaces/$NAMESPACE/pods?labelSelector=app%3Dmme |jq -c '.items[]|.status.podIP'|tr -d '"')

# Set local IP address for diamter, s1ap and s11 networks to the config
jq --arg GTP_IGNITE_LOCAL_IP "$POD_IP" '.gtp.ignite_ip=$GTP_IGNITE_LOCAL_IP' configuration.json > config.tmp && mv config.tmp configuration.json
jq --arg S1AP_IGNITE_LOCAL_IP "$POD_IP" '.s1ap.ignite_ip=$S1AP_IGNITE_LOCAL_IP' configuration.json > config.tmp && mv config.tmp configuration.json
jq --arg S1AP_IGNITE_TARGET_LOCAL_IP "$POD_IP" '.s1ap_target.ignite_ip=$S1AP_IGNITE_TARGET_LOCAL_IP' configuration.json > config.tmp && mv config.tmp configuration.json
jq --arg DIAMETER_IGNITE_LOCAL_IP "$POD_IP" '.diameter.ignite_ip=$DIAMETER_IGNITE_LOCAL_IP' configuration.json > config.tmp && mv config.tmp configuration.json
jq --arg RUNTC_IGNITE_LOCAL_IP "$POD_IP" '.runtestcase.ignite_ip=$RUNTC_IGNITE_LOCAL_IP' configuration.json > config.tmp && mv config.tmp configuration.json
jq --arg GTP_MME_LOCAL_IP "$MME_IP" '.gtp.sut_ip=$GTP_MME_LOCAL_IP' configuration.json > config.tmp && mv config.tmp configuration.json
jq --arg S1AP_MME_LOCAL_IP "$MME_IP" '.s1ap.sut_ip=$S1AP_MME_LOCAL_IP' configuration.json > config.tmp && mv config.tmp configuration.json
jq --arg S1AP_TARGET_MME_LOCAL_IP "$MME_IP" '.s1ap_target.sut_ip=$S1AP_TARGET_MME_LOCAL_IP' configuration.json > config.tmp && mv config.tmp configuration.json
jq --arg DIAMETER_MME_LOCAL_IP "$MME_IP" '.diameter.sut_ip=$DIAMETER_MME_LOCAL_IP' configuration.json > config.tmp && mv config.tmp configuration.json
jq --arg RUNTC_MME_LOCAL_IP "$MME_IP" '.runtestcase.sut_ip=$RUNTC_MME_LOCAL_IP' configuration.json > config.tmp && mv config.tmp configuration.json

cp /opt/ignite/Dev/Common/config/resources.MMEConfig.txt /opt/ignite/Dev/Common/shared/resources.MMEConfig.txt
cd /opt/ignite/Dev/Common/shared/

# Set local ip and MME IP for ROBO TC execution
echo "\${mmeServerIP}    $MME_IP" >> resources.MMEConfig.txt 
echo "\${igniteServerIP}    $POD_IP" >> resources.MMEConfig.txt 

# Copy the final configs for each applications
cp /opt/ignite/Dev/Common/shared/configuration.json /opt/ignite/Dev/Common/configuration.json
cp /opt/ignite/Dev/Common/shared/resources.MMEConfig.txt /opt/ignite/Test/ROBOTCs/resources/resources.MMEConfig.txt

