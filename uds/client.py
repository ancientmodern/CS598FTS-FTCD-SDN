import socket


class UdsClient:
    def __init__(self, server_addr):
        self.server_address = server_addr

    def get(self, dpid, mac_address):
        set_byte = 0x00
        val = self._send_request(set_byte, dpid, mac_address)
        return None if val == 0xFF else val  # if val is 0xFF, the key does not exist

    def set(self, dpid, mac_address, val):
        set_byte = 0x01
        self._send_request(set_byte, dpid, mac_address, val)

    def contains(self, dpid, mac_address):
        return self.get(dpid, mac_address) is not None

    def _send_request(self, set_byte, dpid, mac_address, val=0):
        mac_bytes = bytes.fromhex(mac_address.replace(":", ""))

        if len(mac_bytes) != 6:
            raise ValueError("Invalid MAC address")

        msg = bytearray(10)
        msg[0] = set_byte
        msg[1:3] = dpid.to_bytes(2, "big")
        msg[3:9] = mac_bytes
        msg[9] = val

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.server_address)

        sock.sendall(msg)

        if set_byte == 0x00:
            # Get request
            response = sock.recv(1)
            value = int.from_bytes(response, "big")
            sock.close()
            return value
        else:
            # Set request
            sock.close()
