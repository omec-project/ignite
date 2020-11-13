#
# Copyright (c) 2019, Infosys Ltd.
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

import enum

class ProtocolMessageTypes(enum.Enum):
    attach_accept = enum.auto()
    authentication_info_request = enum.auto()
    authentication_info_response = enum.auto()
    attach_request = enum.auto()
    attach_request_guti = enum.auto()
    authentication_request = enum.auto()
    authentication_response = enum.auto()
    cancel_location_request = enum.auto()
    create_session_request = enum.auto()
    create_session_response = enum.auto()
    delete_session_request = enum.auto()
    delete_session_response = enum.auto()
    detach_accept = enum.auto()
    detach_request = enum.auto()
    downlink_data_notification = enum.auto()
    downlink_data_notification_ack = enum.auto()
    downlink_nas_transport = enum.auto()
    uplink_nas_transport = enum.auto()
    identity_request = enum.auto()
    identity_response = enum.auto()
    initial_context_setup_request = enum.auto()
    initial_context_setup_response = enum.auto()
    modify_bearer_request = enum.auto()
    modify_bearer_response = enum.auto()
    purge_request = enum.auto()
    purge_response = enum.auto()
    release_bearer_request = enum.auto()
    release_bearer_response = enum.auto()
    security_mode_command = enum.auto()
    service_request = enum.auto()
    tau_request = enum.auto()
    ue_context_release_command = enum.auto()
    ue_context_release_complete = enum.auto()
    update_location_request = enum.auto()
    update_location_response = enum.auto()
    esm_information_response = enum.auto()
    handover_required = enum.auto()
    handover_request_acknowledge = enum.auto()
    handover_notify = enum.auto()
    s1_setup_request_target = enum.auto()
    erab_modification_indication = enum.auto()
    securitymode_complete = enum.auto()
    attach_complete = enum.auto()
    create_bearer_request = enum.auto()
    create_bearer_response = enum.auto()
    other_messages = enum.auto()



