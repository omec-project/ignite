#
# Copyright (c) 2020, Infosys Ltd.
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
#

from pysnow import *
import hmac
import hashlib
import binascii
from binascii import hexlify

def createIntegrityKey(int_algo, key):
    b = bytearray.fromhex(key)
    m = bytearray(b'\x15\x02\x00\x01\x01\x00\x01')
    op = hmac.new(b, m, hashlib.sha256).hexdigest().upper()
    ik = bytearray.fromhex(op)[16:]
    return ik.hex()
    
def calculateMac(key, count, bearer, direction, nas_encoded, byteLen):
    key = bytearray.fromhex(key)
    output = snow_f9(key, count, bearer, direction, nas_encoded, byteLen * 8)
    return " ".join(["{:02x}".format(x) for x in output])
