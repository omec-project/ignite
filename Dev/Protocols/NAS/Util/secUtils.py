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