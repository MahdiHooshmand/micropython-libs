from machine import Pin
import time
import network
import socket

# ap = network.WLAN(network.AP_IF)
# ap.config(essid='ESP_TEST', password='1234abcd', authmode=network.AUTH_WPA_WPA2_PSK)
# ap.config(max_clients=10)
# ap.active(True)

in1 = Pin(21, mode=Pin.OUT)
in1.off()
in2 = Pin(32, mode=Pin.OUT)
in2.off()

# while not ap.active():
#     pass
#
# print('Connection successful')
# print(ap.ifconfig())
#
# HOST = "192.168.4.1"
# PORT = 65432
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((HOST, PORT))
# s.listen()
# conn, addr = s.accept()
# print(f"Connected by {addr}")
# while True:
#     data = conn.recv(1024)
#     if not data:
#         break
#     print(data)
# print("close")
# conn.close()
# s.close()
#
# in1 = Pin(21, mode=Pin.OUT)
# in1.off()
# in2 = Pin(32, mode=Pin.OUT)
# in2.on()

while True:
    time.sleep(1)
    in1.on()
    in2.off()
    time.sleep(1)
    in1.off()
    in2.on()
    print("log")
