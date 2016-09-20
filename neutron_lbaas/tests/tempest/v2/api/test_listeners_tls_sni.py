# Copyright 2016 Rackspace US Inc.
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
from keystoneauth1 import identity
from keystoneclient.v2_0 import client as v2_client
from keystoneclient.v3 import client as v3_client
from tempest import config
from tempest.lib.common.utils import data_utils
from tempest.lib import decorators
from tempest.lib import exceptions as ex
from tempest import test
from neutron_lbaas.tests.tempest.v2.api import base
from neutron_lbaas.tests.tempest.v2.common import barbican_helper

config = config.CONF


class TLSSNIListenersTestJSON(base.BaseTestCase):

    """
    Tests the following operations in the Neutron-LBaaS API using the
    REST client for Listeners with TLS:

        list listeners
        create listener
        get listener
        update listener
        delete listener
    """

    @classmethod
    def resource_setup(cls):
        super(TLSSNIListenersTestJSON, cls).resource_setup()
        if not test.is_extension_enabled('lbaas', 'network'):
            msg = "lbaas extension not enabled."
            raise cls.skipException(msg)
        network_name = data_utils.rand_name('network-')
        cls.network = cls.create_network(network_name)
        cls.subnet = cls.create_subnet(cls.network)
        cls.create_lb_kwargs = {'tenant_id': cls.subnet['tenant_id'],
                                'vip_subnet_id': cls.subnet['id']}
        cls.load_balancer = cls._create_active_load_balancer(
            **cls.create_lb_kwargs)
        cls.protocol = 'TERMINATED_HTTPS'
        cls.port = 443
        cls.load_balancer_id = cls.load_balancer['id']

        # Barbican setup
        client_kwargs = {
            'username': config.auth.admin_username,
            'password': config.auth.admin_password,
            'tenant_name': config.auth.admin_project_name,
            'auth_url': config.identity.uri
        }
        if config.identity.auth_version.lower() == 'v2':
            cls.keystone_client = v2_client.Client(**client_kwargs)
        elif config.identity.auth_version.lower() == 'v3':
            client_kwargs['auth_url'] = config.identity.uri_v3
            cls.keystone_client = v3_client.Client(**client_kwargs)
        else:
            raise Exception('Unknown authentication version')

        # TODO(): Keystone should load service endpoint...
        cls.auth = identity.v2.Password(**client_kwargs)

        # create a Keystone session using the auth plugin we just created
        keystone_session = session.Session(auth=cls.auth)

        cls.barbican_client = barbican_client.Client(session=keystone_session)

        cls.barbican_helper = barbican_helper.BarbicanTestHelper(
            cls.barbican_client)
        tls_container_ref = cls.barbican_helper.create_barbican_resources()
        second_tls_container_ref = cls.barbican_helper.create_barbican_resources()
        cls.default_tls_container_ref = tls_container_ref
        cls.sni_tls_container_ref = second_tls_container_ref

        cls.create_listener_kwargs = {
            'loadbalancer_id': cls.load_balancer_id,
            'protocol': cls.protocol,
            'protocol_port': cls.port,
            'default_tls_container_ref': cls.default_tls_container_ref,
            'sni_container_refs': cls.sni_tls_container_ref}
        cls.listener = cls._create_listener(**cls.create_listener_kwargs)
        cls.listener_id = cls.listener['id']



    @test.attr(type='smoke')
    def test_create_tls_sni_listener(self):
        """Test create tls listener"""
        create_new_listener_kwargs = self.create_listener_kwargs
        create_new_listener_kwargs['protocol_port'] = 8081
        new_listener = self._create_listener(
            **create_new_listener_kwargs)
        new_listener_id = new_listener['id']
        self.addCleanup(self._delete_listener, new_listener_id)
        self._check_status_tree(
            load_balancer_id=self.load_balancer_id,
            listener_ids=[self.listener_id, new_listener_id])
        listener = self.listeners_client.get_listener(
            new_listener_id)
        self.assertEqual(new_listener, listener)
        self.assertNotEqual(self.listener, new_listener)


    @test.attr(type='smoke')
    def test_delete_tls_sni_listener(self):
        """Test delete listener"""
        new_tls_container_ref = (
            self.barbican_helper.create_barbican_resources())
        create_new_listener_kwargs = self.create_listener_kwargs
        create_new_listener_kwargs['default_tls_container_ref'] = (
            new_tls_container_ref)
        new_listener = self._create_listener(**create_new_listener_kwargs)
        new_listener_id = new_listener['id']
        self._check_status_tree(
            load_balancer_id=self.load_balancer_id,
            listener_ids=[self.listener_id, new_listener_id])
        listener = self.listeners_client.get_listener(
            new_listener_id)
        self.assertEqual(new_listener, listener)
        self.assertNotEqual(self.listener, new_listener)
        self._delete_listener(new_listener_id)
        self.assertRaises(ex.NotFound,
                          self.listeners_client.get_listener,
                          new_listener_id)
