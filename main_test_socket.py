import time

import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Innostart1401","I#ahosseinpour1401%")
while not wlan.isconnected():
    pass

import socket
HOST = "192.168.43.104"
PORT = 65433

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(socket.getaddrinfo(HOST,PORT)[0][-1])
s.sendall(b"hello from esp")
t.sleep_ms(500)
print(s.recv(1024))
s.close()