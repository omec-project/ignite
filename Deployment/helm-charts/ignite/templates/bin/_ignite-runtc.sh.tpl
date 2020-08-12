#!/bin/bash
#
# Copyright 2019, Infosys Ltd.
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

cp /opt/ignite/Dev/Common/shared/configuration.json /opt/ignite/Dev/Common/configuration.json
cp /opt/ignite/Dev/Common/shared/resources.MMEConfig.txt /opt/ignite/Test/ROBOTCs/resources/resources.MMEConfig.txt

{{- $configJsonRobo := index .Values.config.ignite.cfgFiles "resources.MMEConfig.txt" }}

EXECOPT=$1
if  [[ $EXECOPT == *".py"  || $EXECOPT == *"python"*  ]]; then
	COMMAND="python3 testtpl.py"
	WORKDIR=/opt/ignite/Test/PythonTCs/
	TESTCASENAME=$(basename $EXECOPT .py)
elif  [[ $EXECOPT == *".robot" ||  $EXECOPT == *"robo"* ]]; then
	now=$(date +%Y%m%d_%H%M%S)
	TESTCASENAME=$(basename $EXECOPT .robot)
        MMEPSWD={{index $configJsonRobo "mmePassword"}}
        IGNITEPSWD={{index $configJsonRobo "ignitePassword"}}
	COMMAND="python3 -m robot --variable suitenamecmdline:testtpl_$now  --variable mmePassword:$MMEPSWD --variable ignitePassword:$IGNITEPSWD --outputdir $HOME/LOGS/testtpl/testtpl_$now --timestampoutput testtpl.robot"
	WORKDIR=/opt/ignite/Test/ROBOTCs/testsuites/
	#WORKDIR=/home/lab5g2/omec/mme/source/ignite-project-onf/Test/ROBOTCs/testsuites
	
fi
if [[ $EXECOPT == *"pkg"* ]]; then
	TESTCASENAME=$(cat $WORKDIR/$EXECOPT)
fi
cd $WORKDIR
fail=0
pass=0
for test in $TESTCASENAME
do
   cmd="${COMMAND//testtpl/$test}"
   $cmd | tee /tmp/out.log
   if [[ $cmd == *".py" ]]; then
      grep "Success" /tmp/out.log
      if [[ "$?" == "0" ]]; then
          pass=`expr $pass + 1`
      else 
          fail=`expr $fail + 1`
      fi
   fi
done
if [[ $cmd == *".py" ]]; then
   echo "PASS: $pass"
   echo "FAILED: $fail"
fi
