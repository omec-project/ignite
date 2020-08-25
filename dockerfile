ARG BASE_OS=ubuntu:18.04

FROM quay.io/stackanetes/kubernetes-entrypoint:v0.3.1 as kube-entrypoint
FROM $BASE_OS

COPY ./install_rundeps.sh _sctp.cpython-36m-x86_64-linux-gnu.so per.py /root/
WORKDIR /root
RUN ./install_rundeps.sh
WORKDIR /opt/ignite
RUN mkdir Test && mkdir Dev  && mkdir -p Dev/Common/shared && mkdir -p Test/ROBOTCs/resources/shared
COPY Test Test/
COPY Dev Dev/
RUN chmod 777 Test/ROBOTCs/support_utilities/run.sh
WORKDIR /opt/ignite/scripts
COPY --from=kube-entrypoint /kubernetes-entrypoint  /