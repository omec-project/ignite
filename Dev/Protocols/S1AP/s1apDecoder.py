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

import asn1tools
import time
import sys
import os
from messageType import MESSAGE_TYPE
from iesType import IES_TYPE

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Logger'))
import igniteLogger
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'NAS', 'Decoder'))
import nasDecoder



start = time.time()


def asnDecoding(ie_s, ie_parameter, asn1_obj):
    decoded_data = asn1_obj.decode(ie_s, ie_parameter)
    return decoded_data


def processBytes(bytes_data):
    hex_data = bytes_data.hex()
    return hex_data


def processDict(data, asn1_obj):
    if 'value' in data:
        ie_s = IES_TYPE[str(data['id'])]
        decoded_data = asnDecoding(ie_s, data['value'], asn1_obj)
        if type(decoded_data) == dict:
            data['value'] = processDict(decoded_data, asn1_obj)

    else:
        for key, value in data.items():
            if type(value) == bytes:
                if key == "nAS-PDU" or key == "NAS-PDU":
                    processed_byte = processBytes(value)
                    data[key] = nasDecode(processed_byte)
                else:
                    data[key] = processBytes(value)
            elif type(value) == tuple:
                data[key] = processTuple(value,asn1_obj)
            elif type(value) == list:
                resulted_list = []
                resulted_list.append(processList(value, asn1_obj))
                data[key] = resulted_list
            elif type(value)==dict:
                data[key]= processDict(value,asn1_obj)
    return data


def processList(data, asn1_obj):
    for list_data in range(len(data)):
        if type(data[list_data]) == dict:
            processDict(data[list_data], asn1_obj)
        elif type(data[list_data]) == bytes:
            processed_bytes = processBytes(data[list_data])
            return processed_bytes
    return data


def nasDecode(nasdata):
    decoded_nas = nasDecoder.decode(nasdata)
    return decoded_nas


def processTuple(data,asn1_obj):
    tuple_dict = {}
    tuple_ie = None
    for tuple_value in range(len(data)):
        if type(data[tuple_value]) == bytes:
            data = processBytes(data[tuple_value])
        elif type(data[tuple_value])==dict:
            for t_value in range(len(data)):
                if type(data[t_value])==str:
                    tuple_ie = data[t_value]
                elif type(data[t_value]) == dict:
                    tuple_dict[tuple_ie] = processDict(data[t_value],asn1_obj)
            return tuple_dict
    return data


def Decoding(data, asn1_obj):
	try:
		input_data = bytearray.fromhex(data)
		decoded_data = asnDecoding("S1AP-PDU", input_data, asn1_obj)

		message_type = lambda key: MESSAGE_TYPE[str(key)]
		ie_s = lambda key: IES_TYPE[str(key)]
		message_code = message_type(decoded_data[1]['procedureCode'])

		data_msg = decoded_data[1]
		if type(data_msg) == dict:
			data_message = {}
			decode_value = data_msg['value']
			decoded_msg = asnDecoding(message_code, decode_value, asn1_obj)
			data_message[message_code] = decoded_msg
			data_msg['value'] = data_message
			protocolies_list = decoded_msg['protocolIEs']
			decoded_ies_list = []

			for l in range(len(protocolies_list)):
				decoded_ies = {}
				ies_list = protocolies_list[l]
				ie_code = ie_s(ies_list['id'])
				ies_value = ies_list['value']
				decoded_ie_code = asnDecoding(ie_code, ies_value, asn1_obj)
				if type(decoded_ie_code) == bytes:
					if ie_code == "NAS-PDU":
						processed_byte = processBytes(decoded_ie_code)
						decoded_ies[ie_code] = nasDecode(processed_byte)
					else:
						decoded_ies[ie_code] = processBytes(decoded_ie_code)
				elif type(decoded_ie_code) == dict:
					decoded_ies[ie_code] = processDict(decoded_ie_code, asn1_obj)
				elif type(decoded_ie_code) == int:
					decoded_ies[ie_code] = decoded_ie_code
				elif type(decoded_ie_code) == str:
					decoded_ies[ie_code] = decoded_ie_code
				elif type(decoded_ie_code) == list:
					decoded_ies[ie_code] = processList(decoded_ie_code, asn1_obj)
				elif type(decoded_ie_code) == tuple:
					decoded_ies[ie_code] = processTuple(decoded_ie_code,asn1_obj)

				ies_list['value'] = decoded_ies
				decoded_ies_list.append(ies_list)
			decoded_msg['protocolIEs'] = decoded_ies_list
			data_message[message_code] = decoded_msg
			data_msg['value'] = data_message
		return decoded_data
	
	except Exception as e:
		igniteLogger.logger.info("Printing exception : "f"{e}")
