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
import time
import random
from threading import Thread

setLogLevel('info')

# Two local and one "external" controller (which is actually c0)
# Ignore the warning message that the remote isn't (yet) running
c1 = RemoteController('c1', ip='10.10.1.4', port=6633)
c2 = RemoteController('c2', ip='10.10.1.5', port=6633)
c3 = RemoteController('c3', ip='10.10.1.3', port=6633)
# c4 = RemoteController( 'c4', ip='10.10.1.2', port=6633 )
# c5 = RemoteController( 'c5', ip='10.10.1.6', port=6633 )

# cmap = { 's1': [c1,c2,c3,c4,c5], 's2': [c1,c2,c3,c4,c5], 's3': [c1,c2,c3,c4,c5], 's4': [c1,c2,c3,c4,c5], 's5': [c1,c2,c3,c4,c5], 's6': [c1,c2,c3,c4,c5] }
cmap = {'s1': c1, 's2': c2, 's3': c3}
onlineControllers = {c1, c2, c3}


class MultiSwitch(OVSSwitch):
    "Custom Switch() subclass that connects to different controllers"

    def start(self, controllers):
        if self.name == 's2':
            def isConnected():
                time.sleep(10)
                while True:
                    # isc = self.connected()
                    isc = False
                    uuids = self.controllerUUIDs()
                    print("uuids:", uuids)
                    for uuid in uuids:
                        res = self.vsctl( '-- get Controller', uuid, 'is_connected' )
                        print("uuid: ", uuid, "vsctl info:", res)
                        if 'true' in res: isc = True

                    print("connect info:",isc)
                    if not isc:
                        self.vsctl('del-controller', self.name)
                        print("offline:", cmap[self.name])
                        onlineControllers.remove(cmap[self.name])
                        newCtl = random.choice(list(onlineControllers))
                        print("new one:", newCtl)
                        cmap[self.name] = newCtl
                        self.vsctl('set-controller', self.name, 'tcp:{}:{}'.format(newCtl.ip, newCtl.port))
                        sleep_cnt = 0
                        while self.controllerUUIDs() == uuids:
                            print(sleep_cnt)
                            sleep_cnt += 1
                            time.sleep(1)

            monitor_thread = Thread(target=isConnected)
            monitor_thread.daemon = True
            monitor_thread.start()
        return OVSSwitch.start(self, [cmap[self.name]])


topo = TreeTopo(depth=2, fanout=2)
net = Mininet(topo=topo, switch=MultiSwitch, build=False, waitConnected=True)
for c in [c1, c2, c3]:
    net.addController(c)
net.build()
net.start()

# Modify flow table entries after the network has started
for switch in net.switches:
    # Delete all flow table entries
    switch.dpctl('del-flows')
    # Set the priority of the controller flow entry to 100, ensuring that all flows are directed to the controller
    switch.dpctl('add-flow', 'cookie=0x0,table=0,priority=100,actions=CONTROLLER:65535')

CLI(net)
net.stop()
