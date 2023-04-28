import socket

def get(dpid, mac_address):
    set_byte = 0x00
    return _send_request(set_byte, dpid, mac_address)

def set(dpid, mac_address, val):
    set_byte = 0x01
    _send_request(set_byte, dpid, mac_address, val)

def _send_request(set_byte, dpid, mac_address, val = 0):
    mac_bytes = bytes.fromhex(mac_address.replace(':', ''))

    if len(mac_bytes) != 6:
        raise ValueError("Invalid MAC address")

    msg = bytearray(10)
    msg[0] = set_byte
    msg[1:3] = dpid
    msg[3:9] = mac_bytes
    msg[9] = val

    server_address = '/tmp/sdn-uds.sock'

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(server_address)

    sock.sendall(msg)

    if set_byte == 0x00:  # Get request
        response = sock.recv(1)
        value = int.from_bytes(response, 'big')
        sock.close()
        return value
    else:
        sock.close()
