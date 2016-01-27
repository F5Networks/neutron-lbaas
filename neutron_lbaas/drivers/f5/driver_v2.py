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

import f5lbaasdriver

from oslo_log import log as logging

from neutron_lbaas.drivers import driver_base

VERSION = "0.1.1"
LOG = logging.getLogger(__name__)

class UndefinedEnvironment(Exception):
    pass

class F5PluginV2(driver_base.LoadBalancerBaseDriver):

    def __init__(self, plugin, env=None):
        super(F5PluginV2, self).__init__(plugin)

        self.load_balancer = LoadBalancerManager(self)
        self.listener = ListenerManager(self)
        self.pool = PoolManager(self)
        self.member = MemberManager(self)
        self.health_monitor = HealthMonitorManager(self)

        if not env:
            msg = "F5PluginDriver cannot be intialized because the environment"\
                " is not defined. To set the environment, edit "\
                "neutron_lbaas.conf and append the environment name to the "\
                "service_provider class name."
            LOG.debug(msg)
            raise UndefinedEnvironment(msg)

        LOG.debug("F5PluginDriver: initializing, version=%s, impl=%s, env=%s"
                  % (VERSION, f5lbaasdriver.__version__, env))

        self.impl =  f5lbaasdriver.v2.bigip.plugin_driver.F5DriverV2(
            self, self.plugin.db._core_plugin, env)


class LoadBalancerManager(driver_base.BaseLoadBalancerManager):

    def create(self, context, load_balancer):
        self.driver.impl.lb_create(context, load_balancer)

    def update(self, context, old_load_balancer, load_balancer):
        self.driver.impl.lb_update(context, old_load_balancer, load_balancer)

    def delete(self, context, load_balancer):
        self.driver.impl.lb_delete(context, load_balancer)

    def refresh(self, context, load_balancer):
        self.driver.impl.lb_refresh(context, load_balancer)

    def stats(self, context, load_balancer):
        return self.driver.impl.lb_stats(context, load_balancer)


class ListenerManager(driver_base.BaseListenerManager):

    def create(self, context, listener):
        self.driver.impl.listener_create(context, listener)

    def update(self, context, old_listener, listener):
        self.driver.impl.listener_update(context, old_listener, listener)

    def delete(self, context, listener):
        self.driver.impl.listener_delete(context, listener)


class PoolManager(driver_base.BasePoolManager):

    def create(self, context, pool):
        self.driver.impl.pool_create(context, pool)

    def update(self, context, old_pool, pool):
        self.driver.impl.pool_update(context, old_pool, pool)

    def delete(self, context, pool):
        self.driver.impl.pool_delete(context, pool)


class MemberManager(driver_base.BaseMemberManager):

    def create(self, context, member):
        self.driver.impl.member_create(context, member)

    def update(self, context, old_member, member):
        self.driver.impl.member_update(context, old_member, member)

    def delete(self, context, member):
        self.driver.impl.member_delete(context, member)


class HealthMonitorManager(driver_base.BaseHealthMonitorManager):

    def create(self, context, health_monitor):
        self.driver.impl.healthmonitor_create(context, health_monitor)

    def update(self, context, old_health_monitor, health_monitor):
        self.driver.impl.healthmonitor_update(context, old_health_monitor,
                                   health_monitor)

    def delete(self, context, health_monitor):
        self.driver.impl.healthmonitor_delete(context, health_monitor)
