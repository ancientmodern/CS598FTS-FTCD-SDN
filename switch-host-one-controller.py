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

setLogLevel( 'info' )

# Two local and one "external" controller (which is actually c0)
# Ignore the warning message that the remote isn't (yet) running
c1 = RemoteController( 'c1', ip='10.10.1.4', port=6633 )
# c2 = RemoteController( 'c2', ip='10.10.1.5', port=6633 )
# c3 = RemoteController( 'c3', ip='10.10.1.3', port=6633 )
# c4 = RemoteController( 'c4', ip='10.10.1.2', port=6633 )
# c5 = RemoteController( 'c5', ip='10.10.1.6', port=6633 )

# cmap = { 's1': [c1,c2,c3,c4,c5], 's2': [c1,c2,c3,c4,c5], 's3': [c1,c2,c3,c4,c5], 's4': [c1,c2,c3,c4,c5], 's5': [c1,c2,c3,c4,c5], 's6': [c1,c2,c3,c4,c5] }
cmap = {'s1': [c1], 's2': [c1], 's3': [c1]}


class MultiSwitch( OVSSwitch ):
    "Custom Switch() subclass that connects to different controllers"
    def start( self, controllers ):
        return OVSSwitch.start( self, cmap[ self.name ] )


topo = TreeTopo( depth=2, fanout=2 )
net = Mininet( topo=topo, switch=MultiSwitch, build=False, waitConnected=True )
for c in [c1]:
    net.addController(c)
net.build()
net.start()
CLI( net )
net.stop()
