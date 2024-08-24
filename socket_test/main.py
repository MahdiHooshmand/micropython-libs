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
        while True:
            with open("file.csv", 'a') as file:
                data = conn.recv(1024)
                if not data:
                    break
                print(data)
                file.write(data.decode("utf-8"))
            #conn.send(b"hello from pc")