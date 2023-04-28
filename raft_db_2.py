import socket
from pysyncobj import SyncObj
from mydict import ReplDict
import sys

mac_to_port = ReplDict()
syncObj = SyncObj('node-2:9000', ['node-1:9000', 'node-3:9000'], consumers=[mac_to_port])


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    sock.sendall(msg)

def recvall(sock, n):
    data = bytearray(n)
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a local address and port
# server_address = ('localhost', 12345)
server_address = '/tmp/sdn-uds.sock'
server_socket.bind(server_address)
while True:
    data = recvall(server_socket)
    # get request
    if data[0] == 0x00:
        key = data[1:9]
        val = mac_to_port.get(key)
        # val = mac_to_port[key]
        send_msg(val)
    # set request
    elif data[0] == 0x01:
        key = data[1:9]
        val = data[9]
        # mac_to_port[key] = val
        mac_to_port.set(key, val)
