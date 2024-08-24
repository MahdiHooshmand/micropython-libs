import socket
HOST = "192.168.43.104"
PORT = 65433
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print("bind")
    s.bind((HOST, PORT))
    print("listen")
    s.listen()
    print("accept")
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        with open("persons.csv", 'r') as file:
            for line in file:
                conn.sendall(line.encode("utf-8"))
