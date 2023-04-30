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
from threading import Thread, Event

setLogLevel("info")

# Two local and one "external" controller (which is actually c0)
# Ignore the warning message that the remote isn't (yet) running
c1 = RemoteController("c1", ip="10.10.1.4", port=6633)
c2 = RemoteController("c2", ip="10.10.1.5", port=6633)
c3 = RemoteController("c3", ip="10.10.1.3", port=6633)

cmap = {"s1": c1, "s2": c2, "s3": c3}
onlineControllers = {c1, c2, c3}
carr = [c1, c2, c3]


class MultiSwitch(OVSSwitch):
    "Custom Switch() subclass that connects to different controllers"

    def start(self, controllers):
        self.stop_event = Event()

        def isConnected(stop_event):
            time.sleep(10)
            while not stop_event.is_set():
                # isc = self.connected()
                isc = False
                uuid = self.vsctl("-- get Bridge", self, "Controller").strip()
                uuid = uuid[1:-1]
                res = self.vsctl("-- get Controller", uuid, "is_connected")
                if "true" in res:
                    isc = True

                if not isc:
                    self.vsctl("del-controller", self.name)
                    if cmap[self.name] in onlineControllers:
                        onlineControllers.remove(cmap[self.name])
                    newCtl = random.choice(list(onlineControllers))
                    cmap[self.name] = newCtl
                    self.vsctl(
                        "set-controller",
                        self.name,
                        "tcp:{}:{}".format(newCtl.ip, newCtl.port),
                    )
                    self.dpctl(
                        "add-flow",
                        "cookie=0x0,table=0,priority=100,actions=CONTROLLER:65535",
                    )

                    sleep_cnt = 0
                    new_uuid = self.vsctl("-- get Bridge", self, "Controller").strip()[
                        1:-1
                    ]
                    new_res = self.vsctl("-- get Controller", new_uuid, "is_connected")
                    while not (new_uuid != uuid and "true" in new_res):
                        print(sleep_cnt, new_uuid, new_res)
                        sleep_cnt += 1
                        time.sleep(1)
                        new_uuid = self.vsctl(
                            "-- get Bridge", self, "Controller"
                        ).strip()[1:-1]
                        new_res = self.vsctl(
                            "-- get Controller", new_uuid, "is_connected"
                        )

                    self.dpctl(
                        "add-flow",
                        "cookie=0x0,table=0,priority=100,actions=CONTROLLER:65535",
                    )

        monitor_thread = Thread(target=isConnected, args=(self.stop_event,))
        monitor_thread.daemon = True
        monitor_thread.start()
        idx = (int(self.name[1:]) - 1) // 21
        return OVSSwitch.start(self, [carr[idx]])

    def stop(self, deleteIntfs=True):
        self.stop_event.set()
        super(MultiSwitch, self).stop(deleteIntfs)


topo = TreeTopo(depth=6, fanout=2)
net = Mininet(topo=topo, switch=MultiSwitch, build=False, waitConnected=True)
for c in [c1, c2, c3]:
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
