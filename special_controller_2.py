# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
import time
import numpy as np
from uds import UdsClient


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.latency_list = []
        self.client = UdsClient("/tmp/sdn_uds.sock")
        self.count = 0

    def stop(self):
        with open("logs/ctl_plane_latency.log", "w") as f:
            f.write("\n".join([str(latency) for latency in self.latency_list]))

        minimum = min(self.latency_list)
        maximum = max(self.latency_list)
        average = sum(self.latency_list) / len(self.latency_list)
        mdev = np.std(self.latency_list)
        median = np.median(self.latency_list)
        p50 = np.percentile(self.latency_list, 50)
        p99 = np.percentile(self.latency_list, 99)

        print("\n==================================================")
        print("Min   :", minimum)
        print("Max   :", maximum)
        print("Avg   :", average)
        print("Mdev  :", mdev)
        print("Median:", median)
        print("P50   :", p50)
        print("P99   :", p99)

        super(SimpleSwitch13, self).stop()

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)
        ]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(
                datapath=datapath,
                buffer_id=buffer_id,
                priority=priority,
                match=match,
                instructions=inst,
            )
        else:
            mod = parser.OFPFlowMod(
                datapath=datapath, priority=priority, match=match, instructions=inst
            )
        datapath.send_msg(mod)

        # Log Flow-Mod timestamp
        # flow_mod_time = time.time()
        # return flow_mod_time

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # Log Packet-In timestamp
        packet_in_time = time.time()

        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug(
                "packet truncated: only %s of %s bytes",
                ev.msg.msg_len,
                ev.msg.total_len,
            )
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match["in_port"]

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        # dpid = format(datapath.id, "d").zfill(16)
        dpid = datapath.id  # raw int

        self.logger.info("packet in %d %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        # only write when necessary, as a sync writing is time-consuming
        if in_port != self.client.get(dpid, src):
            self.client.set(dpid, src, in_port)

        # reduce 2 gets to 1 get
        out_port = self.client.get(dpid, dst)
        if out_port is None:
            out_port = ofproto.OFPP_FLOOD

        if dpid <= 21 and self.count < 6000:
            out_port = ofproto.OFPP_FLOOD
            self.count += 1
            self.logger.info(
                "do not learn %d %s %s %s, as count = %d",
                dpid,
                src,
                dst,
                in_port,
                self.count,
            )

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data,
        )
        datapath.send_msg(out)

        control_plane_latency_ms = (time.time() - packet_in_time) * 1000
        self.latency_list.append(control_plane_latency_ms)
        self.logger.info("Control plane latency: %s ms", control_plane_latency_ms)
