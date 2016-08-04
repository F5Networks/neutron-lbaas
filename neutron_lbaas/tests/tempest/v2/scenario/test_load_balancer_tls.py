# Copyright 2015, 2016 Rackspace Inc.
# Copyright 2016 Hewlett Packard Enterprise Development Company
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest import config
from tempest import test

from neutron_lbaas.tests.tempest.v2.scenario import base_tls

config = config.CONF


class TestLoadBalancerTLS(base_tls.BaseTestCaseTLS):

    """This test checks TLS load balancing

    The following is the scenario outline:
    1. Create an instance
    2. SSH to the instance and start two servers
    3. Create a TLS termination load balancer with two members and
       ROUND_ROBIN algorithm, associate the VIP with a floating ip
    4. Send NUM requests to the floating ip and check that they are shared
       between the two servers.
    5. SNI (Create additional certificate(s), add to listener sni, verify
       returned certificates)
    """
    @test.services('compute', 'network')
    def test_load_balancer_tls(self):
        # Test TLS termination
        # Verify HaProxy terminates TLS traffic and sends it to the backend
        self._create_server('server1')
        self._start_servers()
        default_tls_container_ref = self._create_barbican_resources()
        self._create_load_balancer(
            default_tls_container_ref=default_tls_container_ref,
            listener_protocol='TERMINATED_HTTPS',
            port=443,
            pool_protocol='HTTP')
        self._check_load_balancing(protocol='https', port=443)

