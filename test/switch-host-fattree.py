#!/usr/bin/env python
'''
THIS DOES NOT WORK! NEVER RUN THIS!
'''

from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI

setLogLevel('info')

c1 = RemoteController('c1', ip='10.10.1.4', port=6633)
c2 = RemoteController('c2', ip='10.10.1.5', port=6633)
c3 = RemoteController('c3', ip='10.10.1.3', port=6633)

class FatTreeTopo(Topo):
    def __init__(self, k):
        super(FatTreeTopo, self).__init__()

        core_switches = []
        agg_switches = []
        edge_switches = []

        num_pods = k

        # Create core switches
        for i in range((k // 2) ** 2):
            core_switches.append(self.addSwitch(f'cs{i + 1}', dpid=f'000000000000001{i + 1}'))

        # Create aggregation and edge switches, and hosts
        for i in range(num_pods):
            pod_agg_switches = []
            pod_edge_switches = []

            for j in range(k // 2):
                switch_idx = k // 2 * i + j + 1

                # Aggregation switches
                agg_switch = self.addSwitch(f'as{switch_idx}', dpid=f'000000000000002{switch_idx}')
                pod_agg_switches.append(agg_switch)

                # Edge switches
                edge_switch = self.addSwitch(f'es{switch_idx}', dpid=f'000000000000003{switch_idx}')
                pod_edge_switches.append(edge_switch)

                # Hosts
                for h in range(k // 2):
                    host = self.addHost(f'h{k * i + j * (k // 2) + h + 1}', inet6=None)
                    self.addLink(host, edge_switch)

            agg_switches.extend(pod_agg_switches)
            edge_switches.extend(pod_edge_switches)

            # Connect edge switches to aggregation switches
            for j in range(k // 2):
                for l in range(k // 2):
                    self.addLink(edge_switches[k // 2 * i + j], agg_switches[k // 2 * i + l])

            # Connect aggregation switches to core switches
            for j in range(k // 2):
                for l in range(k // 2):
                    # print("agg: {}, core: {}".format(k // 2 * i + j, k // 2 * j + l))
                    self.addLink(agg_switches[k // 2 * i + j], core_switches[k // 2 * j + l])

cmap = {}
for i in range(1, 5):
    cmap[f'cs{i}'] = c1
for i in range(1, 9):
    cmap[f'as{i}'] = c1
for i in range(1, 9):
    cmap[f'es{i}'] = c1

class MultiSwitch(OVSSwitch):
    "Custom Switch() subclass that connects to different controllers"

    def start(self, controllers):
        return OVSSwitch.start(self, [cmap[self.name]])

topo = FatTreeTopo(k=4)
net = Mininet(topo=topo, switch=MultiSwitch, build=False, waitConnected=True)
for c in [c1]:
    net.addController(c)
net.build()
net.start()

for host in net.hosts:
    # disable ipv6
    host.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
    host.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
    host.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

for switch in net.switches:
    # disable ipv6
    switch.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
    switch.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
    switch.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

    # always through controller
    switch.dpctl('del-flows')
    switch.dpctl('add-flow', 'cookie=0x0,table=0,priority=100,actions=CONTROLLER:65535')

CLI(net)
net.stop()
