import socket
HOST = "192.168.43.104"
PORT = 65433

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.connect((HOST,PORT))
    s.sendall(b"hello")
