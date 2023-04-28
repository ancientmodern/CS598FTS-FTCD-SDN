import socket
from pysyncobj import SyncObj
from mydict import ReplDict
import sys

mac_to_port = ReplDict()
syncObj = SyncObj(
    "node-2:9000", ["node-1:9000", "node-3:9000"], consumers=[mac_to_port]
)


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    print("send msg:", msg)
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
server_address = ("localhost", 12345)
# server_address = '/tmp/sdn-uds.sock'
server_socket.bind(server_address)
server_socket.listen(1)
client_socket, address = server_socket.accept()
while True:
    print("Waiting for incoming connections...")
    data = recvall(client_socket, 10)
    print("Connected to", client_socket)
    # get request
    if data[0] == 0x00:
        key = bytes(data[1:9])
        val = mac_to_port.get(key)
        print("get val:", val)
        print("socket:", client_socket)
        send_msg(client_socket, val)
    # set request
    elif data[0] == 0x01:
        key = bytes(data[1:9])
        val = data[9]
        print("set val:", val)
        mac_to_port.set(key, val)
