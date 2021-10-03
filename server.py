import socket
from _thread import *
import ast

server = "192.168.178.75"
port = 6666

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(e)

s.listen(2)
print("Waiting for a connection, Server Started")

idCount = 0

turn = 1

pos_update = {}

def threaded_client(conn, id):
    global turn
    global pos_update
    conn.send(str.encode(str(id)))
    while True:
        try:
            data = conn.recv(2048).decode()

            if data == "get-turn":
                conn.send(str.encode(str(turn)))
                continue

            elif data == "change-turn":
                if turn == 1:
                    turn = 2
                else:
                    turn = 1

            elif "move-figure" in data:

                print(data)

                data = ast.literal_eval(data)

                print(data)

                pos_update = data

            elif data == "get-pos-update":
                if pos_update:
                    conn.send(str.encode(f"{pos_update['move-figure']}, {pos_update['field_id']}"))
                    pos_update.clear()
                    continue

            conn.send(str.encode(" "))

            if not data:
                break

        except Exception as e:
            print(e)

    print("Lost connection")
    conn.close()



while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCount += 1

    start_new_thread(threaded_client, (conn, idCount))