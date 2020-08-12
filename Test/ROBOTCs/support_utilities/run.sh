#! /bin/bash

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

# File: run.sh Usage: ./run.sh Description: To execute the Robo Suites
# Change History
# dd-mm-yyyy : Author - Description
# 12-08-2019 : Vidhya Lakshmi Shankarlal - Initial Version


logDir=$HOME/LOGS

# Create $HOME/LOGS directory,if LOGS folder does not exist
if [ ! -d "$logDir" ]; then
 mkdir $HOME/LOGS
fi

echo "*********************************************"
echo

read -s -p "Enter ignite sudo password: " pswd
echo
read -s -p "Enter mme sudo password: " mmePswd
echo
read -p "Enter Option: s (for single tc execution) or Option: p(for package execution):" execSinglePackOption
echo

execSinglePackOption=${execSinglePackOption,,}

if [ "$execSinglePackOption" == "s" ] ; then
 echo "*****************Suite Names******************"
 echo

 # Find all the suites under testsuites directory and display in console
 find ../testsuites  -type f -name "*.robot" | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | sort

 echo
 echo "**********************************************"
 echo

 read -p "Enter Suite Name from above available option: " suiteName

 echo
        echo "**********************************************"
        echo

 # Create $suiteName directory, if it folder does not exist
 if [ ! -d "$logDir/$suiteName" ]; then
  mkdir $logDir/$suiteName
 fi

 now=$(date +%Y%m%d_%H%M%S)

 # Execute the testsuites
 echo $pswd | sudo -S python3 -m robot --variable suitenamecmdline:$suiteName\_$now --variable mmePassword:$mmePswd --variable ignitePassword:$pswd --outputdir $HOME/LOGS/$suiteName/$suiteName\_$now --timestampoutput ../testsuites/$suiteName.robot

elif [ "$execSinglePackOption" == "p" ] ; then
        echo "*****************Package Name******************"
        echo
		#Find all the available packages under testsuites directory
		grep -Ri "Pkg*" ../testsuites/ | sed s/'    '/'\n'/g | grep -E 'Pkg' | uniq
		echo
		echo "**********************************************"
		echo
		read -p "Enter the Package Name from above available option:" pkgName
        echo
        echo "**********************************************"
        echo

 testSuites=$(echo "$a"|grep -Ril "$pkgName" ../testsuites/ | cut -d '/' -f3 | cut -d '.' -f1)

 for eachSuiteName in $testSuites
 do
         # Create $suiteName directory, if it folder does not exist
  if [ ! -d "$logDir/$eachSuiteName" ]; then
   mkdir $logDir/$eachSuiteName
  fi

  now=$(date +%Y%m%d_%H%M%S)

  echo $pswd | sudo -S python3 -m robot --variable suitenamecmdline:$eachSuiteName\_$now --variable mmePassword:$mmePswd --variable ignitePassword:$pswd --outputdir $HOME/LOGS/$eachSuiteName/$eachSuiteName\_$now --timestampoutput ../testsuites/$eachSuiteName.robot
 done
fi