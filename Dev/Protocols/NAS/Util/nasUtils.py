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


import os, sys, json
currDir = os.path.dirname(__file__)
sys.path.append(os.path.join(currDir, '..', '..', '..', 'Common'))
import igniteCommonUtil as icu


def setNetCap(capbl, nasMsg):	
	ue_ntcap, ue_ntcap_present = icu.getKeyValueFromDict(nasMsg, "ue_network_capability")
	if ue_ntcap_present == "true":
		ue_ntcap[capbl]="supported"

def setTai(mcc,mnc,tac, nasMsg):
    tai_identity, taiPresent = icu.getKeyValueFromDict(nasMsg, "tracking_area_identity")
    if taipresent == "true":
        tai_identity["mcc_digit_1"] = mcc[0]
        tai_identity["mcc_digit_2"] = mcc[1]
        tai_identity["mcc_digit_3"] = mcc[2]
        tai_identity["mnc_digit_1"] = mnc[0]
        tai_identity["mnc_digit_2"] = mnc[1]
        tai_identity["mnc_digit_3"] = mnc[2]
        tai_identity["tac"] = tac

def totalUplinkDownlink(nasMsg):
	
	total_ambr_uplink =0
	total_ambr_downlink =0
	
	apn_ambr,apn_ambr_present = icu.getKeyValueFromDict(nasMsg, "apn_aggregate_maximum_bit_rate")
	
	if apn_ambr_present == "true":
		total_ambr_uplink+=apn_ambr["apn_ambr_for_uplink"]+apn_ambr["apn_ambr_for_uplink_extended"]+apn_ambr["apn_ambr_for_uplink_extended-2"]
		
		total_ambr_downlink+=apn_ambr["apn_ambr_for_downlink"]+apn_ambr["apn_ambr_for_downlink_extended"]+apn_ambr["apn_ambr_for_downlink_extended-2"]
	
	print("TotalUplink :" + total_ambr_uplink +" and TotalDownlink : "+total_ambr_uplink,total_ambr_downlink)

def setImsi(imsi, nasMsg):
    epsmobile_identity, epsmobile_identity_present = icu.getKeyValueFromDict(nasMsg, "eps_mobile_identity")
    if epsmobile_identity_present == "true":
        imsi_digits_list = [int(x) for x in str(imsi)]
        epsmobile_identity["mcc_digit_1_eps"] = imsi_digits_list[0]
        epsmobile_identity["mcc_digit_2_eps"] = imsi_digits_list[1]
        epsmobile_identity["mcc_digit_3_eps"] = imsi_digits_list[2]
        epsmobile_identity["mnc_digit_1_eps"] = imsi_digits_list[3]
        epsmobile_identity["mnc_digit_2_eps"] = imsi_digits_list[4]
        epsmobile_identity["mnc_digit_3_eps"] = imsi_digits_list[5]
        epsmobile_identity["msin_1"] = imsi_digits_list[6]
        epsmobile_identity["msin_2"] = imsi_digits_list[7]
        epsmobile_identity["msin_3"] = imsi_digits_list[8]
        epsmobile_identity["msin_4"] = imsi_digits_list[9]
        epsmobile_identity["msin_5"] = imsi_digits_list[10]
        epsmobile_identity["msin_6"] = imsi_digits_list[11]
        epsmobile_identity["msin_7"] = imsi_digits_list[12]
        epsmobile_identity["msin_8"] = imsi_digits_list[13]
        epsmobile_identity["msin_9"] = imsi_digits_list[14]


def getGuti(nasMsg):
	epsMobileIdentityGuti, epsMobileIdentityGutiPresent = icu.getKeyValueFromDict(nasMsg, "eps_mobile_identity_guti")
	if epsMobileIdentityGutiPresent:
		guti_digits_list = []
		guti_digits_list.append(epsMobileIdentityGuti["mcc_digit_1"])
		guti_digits_list.append(epsMobileIdentityGuti["mcc_digit_2"])
		guti_digits_list.append(epsMobileIdentityGuti["mcc_digit_3"])
		guti_digits_list.append(epsMobileIdentityGuti["mnc_digit_1"])
		guti_digits_list.append(epsMobileIdentityGuti["mnc_digit_2"])
		guti_digits_list.append(epsMobileIdentityGuti["mnc_digit_3"])
		guti_digits_list.append(epsMobileIdentityGuti["mme_group_id"])
		guti_digits_list.append(epsMobileIdentityGuti["mme_code"])
		guti_digits_list.append(epsMobileIdentityGuti["m_tmsi"])
		return guti_digits_list
		
def setGuti(guti_digits_list, nasMsg):
    epsGuti=None
    epsMobileIdentityGuti, epsMobileIdentityGutiDetachPresent = icu.getKeyValueFromDict(nasMsg, "eps_mobile_identity_guti_detach_request")
    if epsMobileIdentityGutiDetachPresent == 'true':
        epsGuti=epsMobileIdentityGuti
    epsMobileIdentityGuti, epsMobileIdentityGutiAttachPresent = icu.getKeyValueFromDict(nasMsg, "eps_mobile_identity_guti_attach_request")
    if epsMobileIdentityGutiAttachPresent == 'true':
        epsGuti=epsMobileIdentityGuti
    if epsMobileIdentityGutiDetachPresent == 'true' or epsMobileIdentityGutiAttachPresent == 'true':
        epsGuti["mcc_digit_1"] = guti_digits_list[0]
        epsGuti["mcc_digit_2"] = guti_digits_list[1]
        epsGuti["mcc_digit_3"] = guti_digits_list[2]
        epsGuti["mnc_digit_1"] = guti_digits_list[3]
        epsGuti["mnc_digit_2"] = guti_digits_list[4]
        epsGuti["mnc_digit_3"] = guti_digits_list[5]
        epsGuti["mme_group_id"] = guti_digits_list[6]
        epsGuti["mme_code"] = guti_digits_list[7]
        epsGuti["m_tmsi"] = guti_digits_list[8]


