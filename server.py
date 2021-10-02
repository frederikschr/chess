import socket
from _thread import *

server = "192.168.178.75"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(e)

s.listen(2)
print("Waiting for a connection, Server Started")

idCount = 0

turn = 1

def threaded_client(conn, id):
    global turn
    conn.send(str.encode(str(id)))
    while True:
        try:
            data = conn.recv(2048).decode()

            if data == "get-turn":
                conn.send(str.encode(str(turn)))

            if data == "change-turn":
                if turn == 1:

                    turn = 2
                else:
                    turn = 1

                conn.send(str.encode("  "))

            if not data:
                break

        except:
            break

    print("Lost connection")
    conn.close()



while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCount += 1

    start_new_thread(threaded_client, (conn, idCount))