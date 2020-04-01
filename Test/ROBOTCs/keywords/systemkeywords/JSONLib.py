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

import json
import sys
sys.path.append('../../../../Dev/Protocols/GTP')
sys.path.append('../../../../Dev/Protocols/S1AP')
sys.path.append('../../../../Dev/Protocols/Diameter')
sys.path.append('../../../../Dev/Common')
import igniteCommonUtil as sy
import asn1tools

class JSONLib(object):    
    def load_json_data_from_file(self,filepath):
    # Load S1AP/NAS Templatess
        data = json.loads(open(filepath).read())
        return data

    def load_templates_from_file(self,filepath):
    # Load GTP Templatess
        msgH, msgD = sy.loadMessageData(filepath)
        return msgH, msgD
   
    def get_asn1_object(self,filepath):
        asn1_obj = asn1tools.compile_files(filepath, 'per', numeric_enums=True)
        return asn1_obj
