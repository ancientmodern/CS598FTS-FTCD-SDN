import socket
import os
import binascii


def decode_mac_address(mac_bytes):
    hex_mac = binascii.hexlify(mac_bytes).decode()
    return ":".join(hex_mac[i : i + 2] for i in range(0, 12, 2))


class ServerBase:
    def __init__(self, server_addr):
        self.server_address = server_addr
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        # Clean up the socket file if it exists
        try:
            os.unlink(self.server_address)
        except OSError:
            if os.path.exists(self.server_address):
                raise

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(self.server_address)

        sock.listen(1)
        print(f"Listen on {self.server_address}")

        while self.running:
            connection, _ = sock.accept()
            response = connection.recv(10)
            set_byte = response[0]
            dpid = int.from_bytes(response[1:3], "big")  # only for print
            mac_address = decode_mac_address(response[3:9])  # only for print
            val = response[9]
            key = response[1:9]  # Directly use bytearrays as keys for efficiency

            if set_byte == 0x00:
                # Get request
                val = self.get_value(key, dpid, mac_address)
                connection.send(val.to_bytes(1, "big"))
            else:
                # Set request
                self.set_value(key, val, dpid, mac_address)

            connection.close()

        sock.close()

    def get_value(self, key, dpid, mac_address):
        raise NotImplementedError

    def set_value(self, key, value, dpid, mac_address):
        raise NotImplementedError


class SimpleServer(ServerBase):
    def __init__(self, server_addr):
        super().__init__(server_addr)
        self.mac_to_port = {}

    def get_value(self, key, dpid, mac_address):
        val = self.mac_to_port.get(key)
        print(f"GET: dpid = {dpid}, mac_address = {mac_address}, get_val: {val}")
        return val if val is not None else 0xFF  # 0xFF means key does not exist

    def set_value(self, key, value, dpid, mac_address):
        print(f"SET: dpid = {dpid}, mac_address = {mac_address}, set_val: {value}")
        self.mac_to_port[key] = value


if __name__ == "__main__":
    server = SimpleServer("/tmp/sdn_uds.sock")
    server.run()
