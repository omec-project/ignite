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

import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Common'))
from protocolMessageTypes import ProtocolMessageTypes as mt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Logger'))
import igniteLogger

diameterMessageDict={
	318:"authentication_info_request",
	317:"cancel_location_response",
	316:"update_location_request",
	321:"purge_request"
	}

diameterRespReqDict={
	"authentication_info_response":"authentication_info_request",
	"update_location_response":"update_location_request",
	"purge_response":"purge_request"
	}

diameterIntialMessages=[mt.cancel_location_request.name]

rat_type_diameter_map={
	"WLAN":0,
	"VIRTUAL":1,
	"UTRAN":1000,
	"GERAN":1001,
	"GAN":1002,
	"HSPA_EVOLUTION":1003,
	"EUTRAN":1004,
	"CDMA2000_1X":2000,
	"HRPD":2001,
	"UMB":2002,
	"EHRPD":2003
	}
		
# Function to add a key to dictionary
def add(msg_data, protocol, op_type, *value):
	if protocol in msg_data:
		if protocol=="dhcp":
			c=0
			message_options = msg_data[protocol]["msg"]["options"]
			for option in message_options:
				if option["code"]!=op_type:
					c+=1
					if c==len(message_options):
						new_option = {}
						new_option["code"]=op_type
						while(len(value))!=0:
							new_option[value[0]]=value[1]
							value=value[2:]
						d_end = msg_data[protocol]["msg"]["options"][-1]
						msg_data[protocol]["msg"]["options"].remove(d_end)
						msg_data[protocol]["msg"]["options"].append(new_option)
						msg_data[protocol]["msg"]["options"].append(d_end)
						break
				else:
					igniteLogger.logger.error('option already present !')
					return None

		elif protocol=="radius":
			c=0
			message_options = msg_data[protocol]["msg"]["attributes"]
			for option in message_options:
				if option["type"]!=op_type:
					c+=1
					if c==len(message_options):
						new_option = {}
						new_option["type"]=op_type
						while(len(value))!=0:
								new_option[value[0]]=value[1]
								value=value[2:]
						msg_data[protocol]["msg"]["attributes"].append(new_option)
						break
				else:
					igniteLogger.logger.error('attribute already present !')
					return None

		elif protocol=="diameter":
			c=0
			message_options = msg_data[protocol]["msg"]["avp"]
			for option in message_options:
				if option["code"]!=op_type:
						c+=1
						if c==len(message_options):
							new_option = {}
							new_option["code"]=op_type
							while(len(value))!=0:
								new_option[value[0]]=value[1]
								value=value[2:]
							msg_data[protocol]["msg"]["avp"].append(new_option)
							break
				else:
					igniteLogger.logger.error('avp already present !')
					return None

		return msg_data
	else:
		return


# Function to replace a key in the dictionary
def replace(msg_data, protocol, key, *value):
	if protocol in msg_data:
		if key in msg_data[protocol]["msg"]:
			if key=="session_id":
				config.setSessionId(value[0])
			elif key=="dstMac":
				config.setDstMac(value[0])
			else:
				msg_data[protocol]["msg"][key]=value[0]
		else:
			if protocol=="ethernet":
				no_of_vlans=len(msg_data[protocol]["msg"]["vlans"])
				if value[0]==1 and value[0]<=no_of_vlans:
					if value[1] in msg_data[protocol]["msg"]["vlans"][0]:
						msg_data[protocol]["msg"]["vlans"][0][value[1]]=value[2]
				elif value[0]==2 and value[0]<=no_of_vlans:
					if value[1] in msg_data[protocol]["msg"]["vlans"][1]:
						msg_data[protocol]["msg"]["vlans"][1][value[1]]=value[2]

			elif(protocol=="dhcp"):
				c = 0
				message_options = msg_data[protocol]["msg"]["options"]
				for option in message_options:
					if key in option:
						option[key] = value[0]
					else:
						c+=1
						if c==len(message_options):
							igniteLogger.logger.error('invalid field. Field not present !')
							return None

			elif(protocol=="radius"):
				c = 0
				attributes = msg_data[protocol]["msg"]["attributes"]
				for attribute in attributes:
					if key in attribute:
						attribute[key] = value[0]
					else:
						c+=1
						if c==len(attributes):
							igniteLogger.logger.error('invalid field. Field not present !')
							return None

			elif(protocol=="diameter"):
				c = 0
				avps = msg_data[protocol]["msg"]["avp"]
				for avp in avps:
					if key in avp:
						if type(avp[key])!=list:
							avp[key] = value[0]
						else:
							d=0
							sub_options = avp[key]
							for subOption in sub_options:
								if value[0] in subOption:
									subOption[value[0]] = value[1]
								else:
									d+=1
									if d==len(sub_options):
										igniteLogger.logger.error('invalid field. Field not present !')
										return None
					else:
						c+=1
						if c==len(avps):
							igniteLogger.logger.error('invalid field. Field not present !')
							return None

		return msg_data

	else:
        	return

# Function to remove a key
def remove(msg_data, protocol, key):
	if protocol=="ethernet":
		vlans=msg_data[protocol]["msg"]["vlans"]
		for vlan in vlans:
			if vlan["tpid"]==key:
				remove_vlan = vlan
				break
		msg_data[protocol]["msg"]["vlans"].remove(remove_vlan)

	elif protocol=="dhcp":
		c=0
		message_options=msg_data[protocol]["msg"]["options"]
		for option in message_options:
			if option["code"]==key:
				rmv_optn = option
				msg_data[protocol]["msg"]["message_options"].remove(rmv_optn)
				break
			else:
				c+=1
				if c==len(message_options):
					igniteLogger.logger.error('invalid field. Field not present !')
					return None
	elif protocol=="radius":
			c=0
			message_attributes=msg_data[protocol]["msg"]["attributes"]
			for attribute in message_attributes:
				if attribute["type"]==key:
					rmv_optn = attribute
					msg_data[protocol]["msg"]["attributes"].remove(rmv_optn)
					break
				else:
					c+=1
					if c==len(message_attributes):
						igniteLogger.logger.error('invalid field. Field not present !')
						return None

	elif protocol=="diameter":
			c=0
			message_avps=msg_data[protocol]["msg"]["avp"]
			for avp in message_avps:
				if avp["code"]==key:
					rmv_optn = avp
					msg_data[protocol]["msg"]["attributes"].remove(rmv_optn)
					break
				else:
					c+=1
					if c==len(message_avps):
						igniteLogger.logger.error('invalid field. Field not present !')
						return None
	else:
		igniteLogger.logger.error("Invalid fields entered. No changes made !")

	return msg_data


# Function to fetch a key
def get(msg_data, protocol, key, *value):
	if protocol in msg_data:
		if key in msg_data[protocol]["msg"]:
			return msg_data[protocol]["msg"][key]
		elif protocol=="dhcp":
			for option in msg_data[protocol]["msg"]["options"]:
				if key in option:
					return option[key]
			igniteLogger.logger.error("Invalid field name")

		elif protocol=="radius":
					for option in msg_data[protocol]["msg"]["attributes"]:
						if key in option:
							return option[key]
					igniteLogger.logger.error("Invalid field name")

		elif protocol=="diameter":
			for option in msg_data[protocol]["msg"]["avp"]:
				if key in option:
					if type(option[key])!=list:
						return option[key]
					else:
						for suboption in option[key]:
							if value[0] in suboption:
								return suboption[value[0]]
			igniteLogger.logger.error("Invalid field name")

	else:
		return


# Function to copy Options from one dictionary to another
def copyConfigOptions(dict1, dict2, protocol):
	dict2[protocol]["msg"]["options"]=dict1[protocol]["msg"]["options"]
	return dict2

def verify(message, protocol, packet):
	code=0	
	if packet=="PADO":
		code = 7
	elif packet=="PADS":
		code = 101
	elif packet=="Configure-Request" or packet=="Authenticate-Request" or packet=="Challenge":
		code = 1
	elif packet=="Configure-Ack" or packet=="Authenticate-Ack" or packet=="Response":
		code = 2
	elif packet=="Configure-Nak" or packet=="Authenticate-Nak" or packet=="Success":
		code = 3
	elif packet=="Configure-Reject" or packet=="Failure":
		code = 4
	elif packet=="Terminate-Request":
		code = 5
	elif packet=="Terminate-Ack":
		code = 6
	elif packet=="Code-Reject":
		code = 7
	elif packet=="Protocol-Reject":
		code = 8
	elif packet=="Echo-Request":
		code = 9
	elif packet=="Echo-Reply":
		code = 10
	elif packet=="Discard-Request":
		code = 11

	if protocol=="pppoe":
		msg_code = get(message, "pppoe", "code")
		session_id = get(message, "pppoe", "session_id")
		if msg_code==code:
			return True
		else:
			return False
	elif protocol=="lcp" or protocol=="ipcp" or protocol=="pap" or protocol=="chap":
		pppoe_code = get(message, "pppoe", "code")
		msg_code = get(message, protocol, "code")
		if pppoe_code==0 and msg_code==code:
			return True
		else:
			return False
	else:
		igniteLogger.logger.error("Invalid protocol")



def setMsgLen(protocol, *value):
	if protocol=="lcp":
		if len(value)==1:
			lcp.setmsgLen(value[0])
		else:
			lcp.setoptionLen(value[0], value[1])
	elif protocol=="ipcp":
		if len(value)==1:
			ipcp.setmsgLen(value[0])
		else:
			ipcp.setoptionLen(value[0], value[1])
	elif protocol=="pap":
		if len(value)==1:
			pap.setmsgLen(value[0])
		else:
			pap.setdataLen(value[0], value[1])
	elif protocol=="chap":
		if len(value)==1:
			chap.setmsgLen(value[0])
		else:
			chap.setvalLen(value[0], value[1])
	else:
		igniteLogger.logger.error("Invalid protocol type !")

