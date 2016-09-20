# Copyright 2015-2016 Hewlett-Packard Development Company, L.P.
# Copyright 2016 Rackspace Inc.
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

from barbicanclient import client as barbican_client
from keystoneauth1 import session
from keystoneclient.v2_0 import client as v2_client
from keystoneclient.v3 import client as v3_client
from oslo_log import log as logging
from tempest import config
from keystoneauth1 import identity
from neutron_lbaas.tests.tempest.v2.common import barbican_helper
from neutron_lbaas.tests.tempest.v2.scenario import base

config = config.CONF

LOG = logging.getLogger(__name__)


class BaseTestCaseTLS(base.BaseTestCase):

    def setUp(self):
        super(BaseTestCaseTLS, self).setUp()
        client_kwargs = {
            'username': config.auth.admin_username,
            'password': config.auth.admin_password,
            'tenant_name': config.auth.admin_project_name,
            'auth_url': config.identity.uri
        }
        if config.identity.auth_version.lower() == 'v2':
            self.keystone_client = v2_client.Client(**client_kwargs)
        elif config.identity.auth_version.lower() == 'v3':
            client_kwargs['auth_url'] = config.identity.uri_v3
            self.keystone_client = v3_client.Client(**client_kwargs)
        else:
            raise Exception('Unknown authentication version')
        keystone_session = session.Session(auth=self.keystone_client)

        # TODO(): Keystone should load service endpoint...
        self.auth = identity.v2.Password(**client_kwargs)

        # create a Keystone session using the auth plugin we just created
        keystone_session = session.Session(auth=self.auth)

        self.barbican_client = barbican_client.Client(session=keystone_session)

        self.barbican_helper = barbican_helper.BarbicanTestHelper(
            self.barbican_client)

    def _cleanup_loadbalancers(self, tls_container_ref=None):
        lbs = self.load_balancers_client.list_load_balancers()
        for lb_entity in lbs:
            lb_id = lb_entity['id']
            lb = self.load_balancers_client.get_load_balancer_status_tree(
                lb_id).get('loadbalancer')
            for listener in lb.get('listeners'):
                for pool in listener.get('pools'):
                    self.delete_wrapper(self.pools_client.delete_pool,
                                        pool.get('id'))
                    self._wait_for_load_balancer_status(lb_id)
                self.delete_wrapper(self.listeners_client.delete_listener,
                                    listener.get('id'))
                self._wait_for_load_balancer_status(lb_id)
                if tls_container_ref:
                    self.cleanup_barbican(tls_container_ref)
            self.delete_wrapper(
                self.load_balancers_client.delete_load_balancer, lb_id)

    def _create_barbican_resources(self):
        tls_container_ref = self.barbican_helper.create_barbican_resources()
        self.assertTrue(tls_container_ref)
        self.addCleanup(self.barbican_helper.cleanup_barbican,
                        tls_container_ref)
        return tls_container_ref

