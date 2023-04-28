import socket
import os
import binascii


def decode_mac_address(mac_bytes):
    hex_mac = binascii.hexlify(mac_bytes).decode()
    return ":".join(hex_mac[i : i + 2] for i in range(0, 12, 2))


class SimpleServer:
    def __init__(self, server_addr):
        self.mac_to_port = {}
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
            dpid = int.from_bytes(response[1:3], "big")
            mac_address = decode_mac_address(response[3:9])
            val = response[9]
            key = response[1:9]  # Directly use bytearrays as keys for efficiency

            print(
                f"Receive set_byte: {set_byte}, dpid: {dpid}, mac_address: {mac_address}, val: {val}"
            )

            if set_byte == 0x00:
                # Get request
                val = self.mac_to_port.get(key)
                val = val if val is not None else 0xFF  # 0xFF means key does not exist
                connection.send(val.to_bytes(1, "big"))
            else:
                self.mac_to_port[key] = val

            connection.close()
