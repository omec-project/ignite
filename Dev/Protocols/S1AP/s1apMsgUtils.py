#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import binascii
import json
from array import *
import os
import sys,random
import requests
import re
import igniteCommonUtil as icu

def generateIeValueForErabModInd(dictToUpdate, tlAddress, gtp_teid_list):
    """
       Takes a dict with nested lists and dicts,
       and searches all dicts for a key of the field
       provided. Once the key is found, update it with new generated value for multiple items
       """
    updated_dict = dictToUpdate
    matched = "false"

    for key, value in dictToUpdate.items():

        if key == 'transportLayerAddress':
            matched = "true"
            keywordPatternMatches = re.search('\$S.*Address$', value)
            if keywordPatternMatches:
                dictToUpdate[key] = tlAddress

        elif key == 'dL-GTP-TEID':
            matched = "true"
            keywordPatternMatches = re.search('\$U.*Teid$', value)
            if keywordPatternMatches:
                dictToUpdate[key] = icu.generateUniqueId('gTP-TEID')
                gtp_teid_list.append(dictToUpdate[key])
                break

        elif isinstance(value, dict):
            updatedDict_1, matched_1 = generateIeValueForErabModInd(value, tlAddress, gtp_teid_list)
            if matched_1 == "true":
                matched = matched_1
                value = updatedDict_1
                dictToUpdate[key] = value
                break

        elif isinstance(value, list):
            for i in range(len(value)):
                if isinstance(value[i], dict):
                    updatedDict_2, matched_2 = generateIeValueForErabModInd(value[i], tlAddress, gtp_teid_list)
                    if matched_2 == "true":
                        matched = matched_2
                        value[i] = updatedDict_2
                        dictToUpdate[key] = value

    updated_dict = dictToUpdate
    return updated_dict, matched


