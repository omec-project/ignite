#
# Copyright (c) 2019, Infosys Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");ttach_S1Release.robot
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
import socket 
from socket import AF_INET , SOCK_DGRAM
import paramiko
import traceback
import os,sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Logger'))
import igniteLogger


def executeCommand(command,ssh_client):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    proc_stat = stdout.read().decode("utf-8")
    return proc_stat

def sshConnect(ip, username, credential, method, timeout=30, port=None):
    
    
    if method not in ['ssh-key', 'ssh-password']:
        raise Exception('Authication must be key or password')

    try:

        if method == 'ssh-password':
            if port is not None:

                client1 = paramiko.SSHClient()
                client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client1.connect(hostname=ip, port=port, username=username,
            					  password=credential, timeout=timeout)
                return client1

            else:
                client1 = paramiko.SSHClient()
                client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client1.connect(hostname=ip,username=username,
                                                  password=credential, timeout=timeout)
                return client1

        else:
            private_key = StringIO(credential)
            if 'RSA' in credential:
            	private_key = paramiko.RSAKey.from_private_key(private_key)
            elif 'DSA' in credential:
            	private_key = paramiko.DSSKey.from_private_key(private_key)
            elif 'EC' in credential:
            	private_key = paramiko.ECDSAKey.from_private_key(private_key)
            elif 'OPENSSH' in credential:
            	private_key = paramiko.Ed25519Key.from_private_key(
            		private_key)
            else:
            	igniteLogger.logger.info(
            		"Unknown or unsupported key type, only support rsa dsa ed25519 ecdsa key type!")

            client1.connect(hostname=ip, port=port, username=username,
            					  key_filename=private_key, timeout=timeout)
            return client1

    except socket.timeout:
        igniteLogger.logger.error('Connect to server {0} time out!'.format(ip))
        return

    except(
    	paramiko.BadHostKeyException,
    	paramiko.AuthenticationException,
    	paramiko.SSHException,
    ) as e:
       igniteLogger.logger.error(traceback.print_exc())
       return

    except Exception as e:
        igniteLogger.logger.error(traceback.print_exc())
        return
		
		
def sshDisconnect(ssh_client):
	if ssh_client:
		ssh_client.close()
