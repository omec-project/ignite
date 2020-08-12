import os,sys,json

sys.path.insert(0, "../../Dev/Protocols/S1AP/")
sys.path.insert(0, "../../Dev/Protocols/GTP/")
sys.path.insert(0, "../../Dev/Protocols/Diameter/")
sys.path.insert(0, "../../Dev/Common/")
sys.path.insert(0, "../../Dev/Protocols/NAS/Util")

import s1apTC as s1
import gtpTC as gs
import diameterTC as ds
import json
import time
import igniteCommonUtil as icu

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Dev', 'Logger'))
import igniteLogger

try:

    #Loading MME details	
    config = json.loads(open('../../Dev/Common/configuration.json').read())
    tcconfig = config["runtestcase"]
    mmeIP = tcconfig["sut_ip"]
    mme_username = tcconfig["mme_username"]
    mme_password = tcconfig["mme_password"]
    mme_lib_path = tcconfig["mme_lib_path"]
    mme_grpc_client_path = tcconfig["mme_grpc_client_path"]
    
    #Loading Stat Types
    stat = json.loads(open('../ROBOTCs/support_utilities/statsTypes.json').read())
    stats_type = stat["stats_type"]
	
    #Generating random values
    imsi = icu.generateUniqueId('imsi')
    enbues1ap_id = icu.generateUniqueId('enbues1apid')
    enbues1ap_id_1 = icu.generateUniqueId('enbues1apid')
    gtp_teid = icu.generateUniqueId('gTP-TEID')
    guti_invalid=icu.generateUniqueId('guti_invalid')

    # Load S1AP Symbols
    initial_ue = json.loads(open('../MessageTemplates/S1AP/initial_uemessage.json').read())
    uplinknastransport_auth_response = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_authresp.json').read())
    uplinknastransport_auth_failure = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_authfailure.json').read())
    uplinknastransport_securitymode_complete = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_securitymodecmp.json').read())
    uplinknastransport_securitymode_reject = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_securitymodereject.json').read())    
    uplinknastransport_esm_information_response = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_esm_information_response.json').read())
    initialcontextsetup_response = json.loads(open('../MessageTemplates/S1AP/initialcontextsetup_response.json').read())
    uplinknastransport_attach_complete = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_attachcmp.json').read())
    uplinknastransport_detach_request = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_detachrequest.json').read())
    uecontextrelease_complete = json.loads(open('../MessageTemplates/S1AP/uecontextrelease_complete.json').read())
    uplinknastransport_tau_request = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_tau_request.json').read())
    uplinknastransport_tau_complete = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_tau_complete.json').read())
    handover_required = json.loads(open('../MessageTemplates/S1AP/handoverrequired.json').read())
    handover_request_acknowledge = json.loads(open('../MessageTemplates/S1AP/handoverrequest_ack.json').read())
    handover_notify = json.loads(open('../MessageTemplates/S1AP/handover_notify.json').read())
    s1_setup_request_target = json.loads(open('../MessageTemplates/S1AP/s1setup_request_target.json').read())
    handover_failure = json.loads(open('../MessageTemplates/S1AP/handover_failure.json').read())
    handover_cancel = json.loads(open('../MessageTemplates/S1AP/handover_cancel.json').read())
    handover_negative_acknowledge = json.loads(open('../MessageTemplates/S1AP/handoverrequest_nack.json').read())
    erabmodification_indication = json.loads(open('../MessageTemplates/S1AP/erabmodification_indication.json').read())

    # Load NAS Symbols
    nas_attach_request = json.loads(open('../MessageTemplates/NAS/attach_request.json').read())
    nas_authentication_response = json.loads(open('../MessageTemplates/NAS/authentication_response.json').read())
    nas_authentication_failure = json.loads(open('../MessageTemplates/NAS/authentication_failure.json').read())
    nas_securitymode_complete = json.loads(open('../MessageTemplates/NAS/security_mode_complete.json').read())
    nas_securitymode_reject = json.loads(open('../MessageTemplates/NAS/security_mode_reject.json').read())    
    nas_esm_information_response = json.loads(open('../MessageTemplates/NAS/esm_information_response.json').read())
    nas_attach_complete = json.loads(open('../MessageTemplates/NAS/attach_complete.json').read())
    nas_detach_request = json.loads(open('../MessageTemplates/NAS/detach_request.json').read())
    nas_tau_request = json.loads(open('../MessageTemplates/NAS/tau_request.json').read())
    nas_tau_complete = json.loads(open('../MessageTemplates/NAS/tau_complete.json').read())
    nas_tau_reject = json.loads(open('../MessageTemplates/NAS/tau_reject.json').read())

    # Load GTP Symbols
    msg_hierarchy, create_session_response = icu.loadMessageData("../MessageTemplates/GTP/create_session_response.json")
    msg_hierarchy, modify_bearer_response = icu.loadMessageData("../MessageTemplates/GTP/modify_bearer_response.json")
    msg_hierarchy, delete_session_response = icu.loadMessageData("../MessageTemplates/GTP/delete_session_response.json")

    # Load Diameter Symbols
    protocol_aia, msg_data_aia = icu.loadMessageData("../MessageTemplates/Diameter/aia.json")
    protocol_ula, msg_data_ula = icu.loadMessageData("../MessageTemplates/Diameter/ula.json")
    protocol_clr, msg_data_clr = icu.loadMessageData("../MessageTemplates/Diameter/clr.json")
    protocol_pua, msg_data_pua= icu.loadMessageData("../MessageTemplates/Diameter/pua.json")

    igniteLogger.logger.info("Messages are loaded successfully")
except Exception as e:
    igniteLogger.logger.error("Printing Exception : "f"{e}")

