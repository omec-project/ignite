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
import sys, requests
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Dev', 'Common'))
import igniteCommonUtil as icu
import sshUtils as su

sys.path.append(os.path.join(os.path.dirname(__file__), '..','ROBOTCs','keywords','systemkeywords'))
import dictOperations as do

clr_flag=False
ssh_client = None

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'MessageTemplates', 'Util'))
    from loadMessage import *
    
    command = "export LD_LIBRARY_PATH=" + mme_lib_path + " && " + mme_grpc_client_path + "/mme-grpc-client mme-app show procedure-stats"
    
    ssh_client = su.sshConnect(mmeIP, mme_username, mme_password, "ssh-password", timeout=10, port=None)
    proc_stat = su.executeCommand(command,ssh_client)
    
    ue_count_before_attach = do.splitProcStats(proc_stat, stats_type["subs_attached"])
    
    #required message templates
    s1_setup_request = json.loads(open('../MessageTemplates/S1AP/s1setup_request.json').read())
    
    print ("\n-------------------------------------\nSetup Started\n---------------------------------------")
    
    igniteLogger.logger.info("\n---------------------------------------\nSend S1Setup Request to MME\n---------------------------------------")
    s1.sendS1ap('s1_setup_request',s1_setup_request,None)
    
    igniteLogger.logger.info("\n---------------------------------------\nS1 Setup Response received from MME\n---------------------------------------")
    s1.receiveS1ap()
    
    time.sleep(1)
    proc_stat_af_detach = su.executeCommand(command,ssh_client)
    
    ue_count_after_detach = do.splitProcStats(proc_stat_af_detach, stats_type["subs_attached"])
    icu.grpcValidation(ue_count_before_attach, ue_count_after_detach, "Number of Subs Attached After Detach")
    
    
    print ("\n-------------------------------------\nSetup Successful\n---------------------------------------")
	
except Exception as e:
    print("**********\nEXCEPTION:"+e.__class__.__name__+"\nError Details : "+str(e)+"\n**********")

	
finally:
    su.sshDisconnect(ssh_client)
    if clr_flag == True:
        igniteLogger.logger.info("\n---------------------------------------\nHSS sends CLR to MME\n---------------------------------------")
        ds.sendS6aMsg('cancel_location_request', msg_data_clr, imsi)

        igniteLogger.logger.info("\n---------------------------------------\nHSS receives CLA from MME\n---------------------------------------")
        ds.receiveS6aMsg()
