#!/bin/bash

set -ex

GATE_DEST=$BASE/new

_DEVSTACK_LOCAL_CONFIG_TAIL=

# Inject config from hook
function load_conf_hook {
    local hook="$1"
    local GATE_HOOKS=$GATE_DEST/neutron-lbaas/neutron_lbaas/tests/contrib/hooks

    _DEVSTACK_LOCAL_CONFIG_TAIL+=$'\n'"$(cat $GATE_HOOKS/$hook)"
}

export DEVSTACK_LOCAL_CONFIG+="
enable_plugin neutron-lbaas https://git.openstack.org/openstack/neutron-lbaas
enable_plugin barbican https://git.openstack.org/openstack/barbican
"

# Sort out our gate args
. $(dirname "$0")/decode_args.sh


function _setup_octavia {
    export DEVSTACK_LOCAL_CONFIG+="
        enable_plugin octavia https://git.openstack.org/openstack/octavia
        "
    if [ "$testenv" != "apiv1" ]; then
        ENABLED_SERVICES+="octavia,o-cw,o-hk,o-hm,o-api,"
    fi
    if [ "$testenv" = "apiv2" ]; then
        load_conf_hook apiv2
    fi

    if [ "$testenv" = "scenario" ]; then
        load_conf_hook scenario
    fi
}


case "$testtype" in

    "tempest")
        # Make sure lbaasv2 is listed as enabled for tempest
        load_conf_hook api_extensions

        # These are not needed with either v1 or v2
        ENABLED_SERVICES+="-c-api,-c-bak,-c-sch,-c-vol,-cinder,"
        ENABLED_SERVICES+="-s-account,-s-container,-s-object,-s-proxy,"

        if [ "$testenv" != "scenario" ]; then
            export DEVSTACK_LOCAL_CONFIG+="
        DISABLE_AMP_IMAGE_BUILD=True
        "
            # Not needed for API tests
            ENABLED_SERVICES+="-horizon,-ceilometer-acentral,-ceilometer-acompute,"
            ENABLED_SERVICES+="-ceilometer-alarm-evaluator,-ceilometer-alarm-notifier,"
            ENABLED_SERVICES+="-ceilometer-anotification,-ceilometer-api,"
            ENABLED_SERVICES+="-ceilometer-collector,"
        fi

        if [ "$testenv" != "apiv1" ]; then
            # Override enabled services, so we can turn on lbaasv2.
            # While we're at it, disable cinder and swift, since we don't need them.
            ENABLED_SERVICES+="q-lbaasv2,-q-lbaas,"

            if [ "$lbaasdriver" = "namespace" ]; then
                export DEVSTACK_LOCAL_CONFIG+="
        NEUTRON_LBAAS_SERVICE_PROVIDERV2=LOADBALANCERV2:Haproxy:neutron_lbaas.drivers.haproxy.plugin_driver.HaproxyOnHostPluginDriver:default
        "
             fi
        fi

        if [ "$lbaasdriver" = "octavia" ]; then
            _setup_octavia
        fi

        export ENABLED_SERVICES
        export DEVSTACK_LOCAL_CONFIG+=$'\n'"$_DEVSTACK_LOCAL_CONFIG_TAIL"
        ;;

    *)
        echo "Unrecognized test type $testtype".
        exit 1
        ;;
esac


"$GATE_DEST"/devstack-gate/devstack-vm-gate.sh
