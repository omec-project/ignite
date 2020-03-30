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
    #Generating random values
    imsi = icu.generateUniqueId('imsi')
    enbues1ap_id = icu.generateUniqueId('enbues1apid')
    enbues1ap_id_1 = icu.generateUniqueId('enbues1apid')
    gtp_teid = icu.generateUniqueId('gTP-TEID')
    guti_invalid=icu.generateUniqueId('guti_invalid')

    # Load S1AP Symbols
    initial_ue = json.loads(open('../MessageTemplates/S1AP/initial_uemessage.json').read())
    uplinknastransport_auth_response = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_authresp.json').read())
    uplinknastransport_securitymode_complete = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_securitymodecmp.json').read())
    uplinknastransport_esm_information_response = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_esm_information_response.json').read())
    initialcontextsetup_response = json.loads(open('../MessageTemplates/S1AP/initialcontextsetup_response.json').read())
    uplinknastransport_attach_complete = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_attachcmp.json').read())
    uplinknastransport_detach_request = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_detachrequest.json').read())
    uecontextrelease_complete = json.loads(open('../MessageTemplates/S1AP/uecontextrelease_complete.json').read())

    # Load NAS Symbols
    nas_attach_request = json.loads(open('../MessageTemplates/NAS/attach_request.json').read())
    nas_authentication_response = json.loads(open('../MessageTemplates/NAS/authentication_response.json').read())
    nas_securitymode_complete = json.loads(open('../MessageTemplates/NAS/security_mode_complete.json').read())
    nas_esm_information_response = json.loads(open('../MessageTemplates/NAS/esm_information_response.json').read())
    nas_attach_complete = json.loads(open('../MessageTemplates/NAS/attach_complete.json').read())
    nas_detach_request = json.loads(open('../MessageTemplates/NAS/detach_request.json').read())

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
    igniteLogger.logger.info("Printing Exception : "f"{e}")

