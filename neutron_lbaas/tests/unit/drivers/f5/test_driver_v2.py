# Copyright 2016 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys

import mock
from neutron import context

from neutron_lbaas.tests.unit.db.loadbalancer import test_db_loadbalancerv2

with mock.patch.dict(sys.modules, {'f5lbaasdriver': mock.Mock(__version__="0.1.1")}):
    from neutron_lbaas.drivers.f5 import driver_v2


class FakeModel(object):
    def __init__(self, id):
        self.id = id


class TestF5PluginV2(test_db_loadbalancerv2.LbaasPluginDbTestCase):
    """Unit tests for F5 LBaaSv2 plugin driver.

    All tests follow the same pattern: call plugin method and test
    that plugin delegated request to its driver implementation object.

    To test independent of full neutron-lbaas test suite:
        tox -e py27 -- neutron_lbaas.tests.unit.drivers.f5
    """

    def setUp(self):
        super(TestF5PluginV2, self).setUp()
        plugin = mock.Mock()
        core_plugin = mock.Mock()

        self.driver = driver_v2.F5PluginV2(plugin, core_plugin)
        self.driver.impl = mock.Mock()
        self.context = context.get_admin_context()

    def test_load_balancer_manager(self):
        model = FakeModel("loadbalancer-01")
        new_model = FakeModel("loadbalancer-02")

        self.driver.load_balancer.create(self.context, model)
        self.driver.impl.lb_create.assert_called_with(self.context, model)

        self.driver.load_balancer.update(self.context, model, new_model)
        self.driver.impl.lb_update.assert_called_with(
            self.context, model, new_model)

        self.driver.load_balancer.delete(self.context, model)
        self.driver.impl.lb_delete.assert_called_with(
            self.context, model)

        self.driver.load_balancer.refresh(self.context, model)
        self.driver.impl.lb_refresh.assert_called_with(
            self.context, model)

        self.driver.load_balancer.stats(self.context, model)
        self.driver.impl.lb_stats.assert_called_with(
            self.context, model)

    def test_listener_manager(self):
        model = FakeModel("listener-01")
        new_model = FakeModel("listener-02")

        self.driver.listener.create(self.context, model)
        self.driver.impl.listener_create.assert_called_with(
            self.context, model)

        self.driver.listener.update(self.context, model, new_model)
        self.driver.impl.listener_update.assert_called_with(
            self.context, model, new_model)

        self.driver.listener.delete(self.context, model)
        self.driver.impl.listener_delete.assert_called_with(
            self.context, model)

    def test_pool_manager(self):
        model = FakeModel("pool-01")
        new_model = FakeModel("pool-02")
        self.driver.pool.create(self.context, model)
        self.driver.impl.pool_create.assert_called_with(
            self.context, model)

        self.driver.pool.update(self.context, model, new_model)
        self.driver.impl.pool_update.assert_called_with(
            self.context, model, new_model)

        self.driver.pool.delete(self.context, model)
        self.driver.impl.pool_delete.assert_called_with(
            self.context, model)

    def test_member_manager(self):
        model = FakeModel("member-01")
        new_model = FakeModel("member-02")

        self.driver.member.create(self.context, model)
        self.driver.impl.member_create.assert_called_with(
            self.context, model)

        self.driver.member.update(self.context, model, new_model)
        self.driver.impl.member_update.assert_called_with(
            self.context, model, new_model)

        self.driver.member.delete(self.context, model)
        self.driver.impl.member_delete.assert_called_with(
            self.context, model)

    def test_health_monitor_manager(self):
        model = FakeModel("healthmonitor-01")
        new_model = FakeModel("healthmonitor-02")

        self.driver.health_monitor.create(self.context, model)
        self.driver.impl.healthmonitor_create.assert_called_with(
            self.context, model)

        self.driver.health_monitor.update(self.context, model, new_model)
        self.driver.impl.healthmonitor_update.assert_called_with(
            self.context, model, new_model)

        self.driver.health_monitor.delete(self.context, model)
        self.driver.impl.healthmonitor_delete.assert_called_with(
            self.context, model)
