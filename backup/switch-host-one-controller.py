#!/usr/bin/env python

"""
Create a network where different switches are connected to
different controllers, by creating a custom Switch() subclass.
"""

from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.topolib import TreeTopo
from mininet.log import setLogLevel
from mininet.cli import CLI

setLogLevel("info")

# Two local and one "external" controller (which is actually c0)
# Ignore the warning message that the remote isn't (yet) running
c1 = RemoteController("c1", ip="10.10.1.4", port=6633)

cmap = {"s1": [c1], "s2": [c1], "s3": [c1]}


class MultiSwitch(OVSSwitch):
    "Custom Switch() subclass that connects to different controllers"

    def start(self, controllers):
        return OVSSwitch.start(self, cmap[self.name])


topo = TreeTopo(depth=2, fanout=2)
net = Mininet(topo=topo, switch=MultiSwitch, build=False, waitConnected=True)
for c in [c1]:
    net.addController(c)
net.build()
net.start()

# Modify flow table entries after the network has started
for switch in net.switches:
    # Delete all flow table entries
    switch.dpctl("del-flows")
    # Set the priority of the controller flow entry to 100, ensuring that all flows are directed to the controller
    switch.dpctl("add-flow", "cookie=0x0,table=0,priority=100,actions=CONTROLLER:65535")

CLI(net)
net.stop()
