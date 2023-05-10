import argparse
from pysyncobj import SyncObj
from mydict import ReplDict
from uds import ServerBase


class RaftDBServer(ServerBase):
    def __init__(self, server_addr, leader, followers):
        super().__init__(server_addr)
        self.mac_to_port = ReplDict()
        self.syncObj = SyncObj(leader, followers, consumers=[self.mac_to_port])

    def get_value(self, key, dpid, mac_address):
        val = self.mac_to_port.get(key)
        print(f"GET: dpid = {dpid}, mac_address = {mac_address}, get_val: {val}")
        return val if val is not None else 0xFF

    def set_value(self, key, value, dpid, mac_address):
        print(f"SET: dpid = {dpid}, mac_address = {mac_address}, set_val: {value}")
        self.mac_to_port.set(key, value, sync=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the server.")
    parser.add_argument("--leader", help="Leader for the raft server.")
    parser.add_argument("--followers", nargs="+", help="Followers for the raft server.")
    args = parser.parse_args()

    if args.leader is None or args.followers is None:
        raise ValueError("Leader and followers must be provided for raft server.")
    server = RaftDBServer("/tmp/sdn_uds.sock", args.leader, args.followers)

    server.run()
