#!/bin/bash
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

SUDO=''
[[ $EUID -ne 0 ]] && SUDO=sudo

install_run_pkg_deps() {
        $SUDO apt-get update && $SUDO apt-get install -y \
        python3 \
        python3-dev \
        python3-pip \
        libsctp-dev \
        net-tools \
        vim \
        jq \
        curl \
        git \
        openssh-server \
        zip \
        tcpdump \
        sudo
       }

install_run_dep_lib() {
        $SUDO python3 -m pip install \
        asn1tools==0.137.4 \
        xlrd \
        pysctp \
        robotframework \
        robotframework-sshlibrary \
        robotframework-requests \
        flask
}

install_crypto_mobile() {
	   cd /tmp/ \
	&& git clone https://github.com/mitshell/CryptoMobile.git \
	&& cd CryptoMobile \
	&& $SUDO python3 setup.py install \
	&& cd /root/
}

install_lib_patch() {
        mv /usr/local/lib/python3.6/dist-packages/_sctp.cpython-36m-x86_64-linux-gnu.so /usr/local/lib/python3.6/dist-packages/_sctp.cpython-36m-x86_64-linux-gnu.so_orig
        cp _sctp.cpython-36m-x86_64-linux-gnu.so /usr/local/lib/python3.6/dist-packages/
        mv /usr/local/lib/python3.6/dist-packages/asn1tools/codecs/per.py /usr/local/lib/python3.6/dist-packages/asn1tools/codecs/per.py_orig
        cp per.py /usr/local/lib/python3.6/dist-packages/asn1tools/codecs/
}

install_ssh_server() {
        $SUDO mkdir /var/run/sshd
        echo 'root:mypass' | chpasswd
        sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
        sed -i 's/#PermitRootLogin yes/PermitRootLogin yes/' /etc/ssh/sshd_config
        sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
        echo "export VISIBLE=now" >> /etc/profile
}

install() {
        install_run_pkg_deps
        install_run_dep_lib
        install_crypto_mobile
        install_ssh_server
        install_lib_patch
}

(return 2>/dev/null) && echo "Sourced" && return

set -o errexit
set -o pipefail
set -o nounset

install

echo "Dependency installation complete"
