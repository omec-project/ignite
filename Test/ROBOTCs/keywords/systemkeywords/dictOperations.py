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
from array import *

def getChildKeyValueFromParentKey(mydata,parentkey,key):
# This function searches for all occurance of key in a dictinory and returns the valueList, The input arguments are dictionary data, parentkey and childkey to search
    keyValue = None
    if type(mydata) is dict:
        for mykey,value in mydata.items():
            if parentkey:
                if mykey == parentkey:
                    return getChildKeyValueFromParentKey(value,None,key)
                elif type(value) is dict or type(value) is list:
                    keyValue= getChildKeyValueFromParentKey(value,parentkey,key)
                    if keyValue:
                        return keyValue
            elif mykey == key:
                return value
            elif type(value) is dict or type(value) is list:
                keyValue = getChildKeyValueFromParentKey(value,parentkey,key)
            if keyValue:
                break
    elif type(mydata) is list:
        for entry in mydata:
            keyValue = getChildKeyValueFromParentKey(entry,parentkey,key)
            if keyValue:
                break
    return keyValue

def getAllInstanceKeyValue(mydata,key,valueList=None):
# This function searches for all occurance of key in a dictinory and returns the valueList, The input arguments are dictionary data, key to search
    if valueList is None:
        valueList=[]
    ret = None
    if type(mydata) is dict:
        for mykey,value in mydata.items():
            if mykey == key:
                valueList.append(value)
            if type(value) is dict or type(value) is list:
                getAllInstanceKeyValue(value,key,valueList)
                if mykey == key:
                    valueList.append(value)
    elif type(mydata) is list:
        for entry in mydata:
            getAllInstanceKeyValue(entry,key,valueList)
    return valueList

def splitProcStats(stats,string):
    allValList = stats.split()
    count = 0
    for index,eachVal in enumerate(allValList):
        if eachVal == string:
            count = int(allValList[index+1])
            break
    return count

